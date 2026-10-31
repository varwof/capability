// Cross-language EMILIA binding projection probe (TypeScript).
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..', '..');
const FIXTURE = process.env.CLC_EMILIA_BINDING_FIXTURE
  || path.resolve(ROOT, '..', 'register', 'cmd', 'emilia-projection-probe',
    'testdata', 'emilia-binding-fixture-v1.json');
// Resolved beside the binding fixture so a caller that points
// CLC_EMILIA_BINDING_FIXTURE at a non-sibling checkout still finds the schema.
const SCHEMA_FIXTURE = process.env.CLC_EMILIA_SCHEMA_FIXTURE
  || path.join(path.dirname(FIXTURE), 'emilia-binding-fixture-v2.json');
const CLC_TS_FILE = process.env.CLC_TS_FILE
  || path.resolve(ROOT, '..', 'aic-capability-demo', 'ts', 'clc_semantics.ts');
const CLC_TS_URL = CLC_TS_FILE.startsWith('file://')
  ? new URL(CLC_TS_FILE) : pathToFileURL(CLC_TS_FILE);
const clc = await import(CLC_TS_URL.href);
const evidence = await import(new URL('./evidence_semantics.ts', CLC_TS_URL).href);

const digestObject = (value) =>
  'sha-256:' + createHash('sha256')
    .update(Buffer.from(clc.canonicalJSON(value), 'utf8'))
    .digest('hex');

const utf8Compare = (a, b) =>
  Buffer.compare(Buffer.from(a, 'utf8'), Buffer.from(b, 'utf8'));

function canonicalArtifactSet(targets) {
  if (targets.length === 0) {
    throw new Error('artifact set is empty');
  }
  const encoded = targets.map((target) => (
    [Buffer.from(clc.canonicalJSON(target), 'utf8'), target]));
  encoded.sort((left, right) => Buffer.compare(left[0], right[0]));
  for (let i = 1; i < encoded.length; i += 1) {
    if (Buffer.compare(encoded[i - 1][0], encoded[i][0]) === 0) {
      throw new Error('artifact set contains duplicate members');
    }
  }
  for (const [, target] of encoded) {
    if (typeof target.type !== 'string' || target.type.length === 0) {
      throw new Error('artifact set member has no type');
    }
  }
  const types = new Set(encoded.map(([, target]) => target.type));
  if (types.size > 1) {
    throw new Error('artifact set mixes target types');
  }
  return encoded.map(([, target]) => target);
}

function relationTuple(binding) {
  const targets = canonicalArtifactSet(binding.targets);
  const subjects = targets.map((target) => target.subject).sort(utf8Compare);
  const issuedAt = [binding.source.issued_at,
    ...targets.map((target) => target.issued_at)].sort(utf8Compare);
  return {
    requirement_digest: binding.requirement_digest,
    policy_generation: binding.source.policy_generation,
    from: {
      type: binding.source.type,
      artifact_digest: digestObject(binding.source),
    },
    relation: binding.relation,
    to: {
      type: targets[0].type,
      artifact_set_digest: digestObject(targets),
    },
    action_digest: digestObject(binding.action),
    subjects,
    trust: binding.trust,
    trust_snapshot_digest: binding.trust_snapshot_digest,
    status_digest: digestObject(binding.status),
    status_snapshot: binding.status,
    evidence_issued_at: issuedAt,
  };
}

const bindingSubject = (binding) => createHash('sha256')
  .update(Buffer.from(clc.canonicalJSON(relationTuple(binding)), 'utf8'))
  .digest('base64url');

function mutate(binding, mutation) {
  const value = JSON.parse(JSON.stringify(binding));
  const parts = mutation.path;
  let current = value;
  for (const part of parts.slice(0, -1)) current = current[part];
  current[parts.at(-1)] = mutation.value;
  return value;
}

function evidenceFacts(testCase, now, subject) {
  const facts = [];
  const roles = Object.keys(testCase.facts).sort(utf8Compare);
  for (const role of roles) {
    for (const entry of testCase.facts[role]) {
      facts.push({
        type: role,
        subject: entry.subject === '$binding' ? subject : entry.subject,
        verified: entry.verified,
        issued_at: new Date(
          Date.parse(now) - entry.age_sec * 1000
        ).toISOString(),
      });
    }
  }
  return facts;
}

const verdictString = (verdict, reason) => verdict + (reason ? `/${reason}` : '');

function printCase(id, name, want, got, expectedGot = want) {
  const status = got === expectedGot ? 'PASS' : 'FAIL';
  console.log(`${status} ${id} ${name.padEnd(55)} want=${want} got=${got}`);
}

const ROLE_MAP = {
  'ep-human-authorization': 'ep-quorum',
  'ep-quorum': 'ep-quorum',
  'policy-permit': 'policy-permit',
};

const AEC_VERSION = 'EP-AEC-REQUIREMENT-v1';
const AEC_TOP = new Set([
  '@version', 'requirement_id', 'purpose', 'expression', 'freshness_sec',
  'status_required', 'role_constraints', 'required_bindings',
]);
const AEC_ROLE_CONSTRAINT = new Set([
  'type', 'component_type', 'threshold', 'subject_id_source',
]);
const AEC_BINDING = new Set(['from_type', 'relation', 'to_type']);
const AEC_IDENT = /^[A-Za-z0-9._:-]+$/;

function checkAecMembers(source) {
  for (const key of Object.keys(source)) {
    if (!AEC_TOP.has(key)) throw new Error(`unknown AEC member ${key}`);
  }
  for (const [index, rc] of (source.role_constraints ?? []).entries()) {
    for (const key of Object.keys(rc)) {
      if (!AEC_ROLE_CONSTRAINT.has(key)) {
        throw new Error(`role_constraints[${index}] unknown member ${key}`);
      }
    }
  }
  for (const [index, binding] of (source.required_bindings ?? []).entries()) {
    for (const key of Object.keys(binding)) {
      if (!AEC_BINDING.has(key)) {
        throw new Error(`required_bindings[${index}] unknown member ${key}`);
      }
    }
  }
}

function checkAecIdentifier(field, value) {
  if (typeof value !== 'string' || !AEC_IDENT.test(value)) {
    throw new Error(`AEC ${field} is outside the identifier set`);
  }
}

function mapRole(role) {
  if (!Object.prototype.hasOwnProperty.call(ROLE_MAP, role)) {
    throw new Error(`AEC role ${role} has no pinned CLC mapping`);
  }
  return ROLE_MAP[role];
}

function bindingRoleName(fromType, relation, toType) {
  const parts = [fromType, relation, toType].map((part) => {
    const bytes = Buffer.from(part, 'utf8');
    if (bytes.length > 256) {
      throw new Error('AEC required_bindings part is too long');
    }
    const len = Buffer.alloc(4);
    len.writeUInt32BE(bytes.length);
    return Buffer.concat([len, bytes]);
  });
  const role = 'clc:evidence-binding:'
    + Buffer.concat(parts).toString('base64url');
  if (role.length > 256) {
    throw new Error('encoded binding role exceeds 256 bytes');
  }
  return role;
}

function projectAec(source) {
  if (source['@version'] !== AEC_VERSION) {
    throw new Error(`unsupported AEC version ${source['@version']}`);
  }
  checkAecMembers(source);
  if (!source.requirement_id) throw new Error('AEC requirement_id is required');
  const constraints = [];
  const freshness = source.freshness_sec ?? {};
  const roles = Object.keys(freshness).sort(
    (a, b) => Buffer.compare(Buffer.from(a, 'utf8'), Buffer.from(b, 'utf8')),
  );
  for (const role of roles) {
    constraints.push({
      role: mapRole(role),
      constraint: `varwof/evidence-v1:freshness:sec:${freshness[role]}`,
    });
  }
  for (const rc of source.role_constraints ?? []) {
    if (rc.type !== 'distinct-subject-quorum') {
      throw new Error(`unsupported role constraint ${rc.type}`);
    }
    if (rc.subject_id_source !== 'native-verifier') {
      throw new Error('subject_id_source must be native-verifier');
    }
    constraints.push({
      role: mapRole(rc.component_type),
      constraint: `varwof/evidence-v1:quorum:distinct:${rc.threshold}`,
    });
  }

  for (const role of source.status_required ?? []) {
    if (!role || !Object.prototype.hasOwnProperty.call(ROLE_MAP, role)) {
      throw new Error(`AEC status_required role ${role} has no pinned mapping`);
    }
  }

  const parts = [`(${source.expression})`];
  const seen = new Set();
  for (const binding of source.required_bindings ?? []) {
    for (const field of ['from_type', 'relation', 'to_type']) {
      checkAecIdentifier(field, binding[field]);
    }
    const role = bindingRoleName(
      binding.from_type, binding.relation, binding.to_type,
    );
    if (!seen.has(role)) {
      parts.push(role);
      seen.add(role);
    }
  }

  const out = {
    '@version': 'CLC-REQUIREMENT-v1',
    requirement_id: source.requirement_id,
  };
  if (source.purpose) out.purpose = source.purpose;
  out.expression = parts.join(' AND ');
  if (Buffer.byteLength(out.expression, 'utf8') > 512) {
    throw new Error('projected expression exceeds the CLC 512-byte limit');
  }
  if (constraints.length > 0) out.constraints = constraints;
  return out;
}

function requirementDigest(value) {
  return 'sha-256:'
    + createHash('sha256')
      .update(Buffer.from(clc.canonicalJSON(value), 'utf8'))
      .digest('hex');
}

function schemaCarrierError(schemaFixture, binding, results) {
  const document = schemaFixture.status_schema_document;
  if (!document || typeof document !== 'object' || Object.keys(document).length === 0) {
    throw new Error('status_schema_document is missing');
  }
  const acceptedRaw = schemaFixture.accepted_status_schema_digests;
  if (!Array.isArray(acceptedRaw) || acceptedRaw.length === 0) {
    throw new Error('accepted_status_schema_digests is empty');
  }
  const docDigest = digestObject(document);
  const docId = document.$id;
  const accepted = new Set();
  for (const digest of acceptedRaw) {
    if (typeof digest !== 'string' || digest.length === 0) {
      throw new Error('accepted schema digest is empty');
    }
    accepted.add(digest);
  }
  if (!Array.isArray(binding.targets) || binding.targets.length === 0) {
    throw new Error('target set is empty');
  }
  const properties = document.properties;
  const docType = properties && properties.type && typeof properties.type.const === 'string'
    ? properties.type.const : null;
  const members = new Map();
  for (const target of binding.targets) {
    const artifactId = target.artifact_id;
    if (typeof artifactId !== 'string' || artifactId.length === 0) {
      throw new Error('target has no artifact_id');
    }
    if (members.has(artifactId)) {
      throw new Error(`duplicate target artifact_id ${artifactId}`);
    }
    if (docType !== null && target.type !== docType) {
      throw new Error(`target ${artifactId}: type does not match the pinned schema type`);
    }
    const schema = target.status_schema;
    if (!schema || typeof schema !== 'object') {
      throw new Error(`target ${artifactId}: missing status_schema`);
    }
    for (const key of ['id', 'version', 'digest']) {
      if (typeof schema[key] !== 'string' || schema[key].length === 0) {
        throw new Error(`target ${artifactId}: status_schema.${key} is empty`);
      }
    }
    if (typeof docId === 'string' && docId.length > 0 && schema.id !== docId) {
      throw new Error(`target ${artifactId}: status_schema.id does not name the pinned document`);
    }
    if (schema.digest !== docDigest) {
      throw new Error(`target ${artifactId}: schema digest does not pin the document`);
    }
    if (!accepted.has(schema.digest)) {
      throw new Error(`target ${artifactId}: schema digest is not accepted`);
    }
    members.set(artifactId, schema);
  }
  for (const result of results) {
    const artifactId = result.artifact_id;
    if (typeof artifactId !== 'string' || artifactId.length === 0) {
      throw new Error('native result has no artifact_id');
    }
    const targetSchema = members.get(artifactId);
    if (!targetSchema) {
      throw new Error(`result ${artifactId}: carrier is not in the target set`);
    }
    if (digestObject(result.status_schema) !== digestObject(targetSchema)) {
      throw new Error(`result ${artifactId}: schema identity differs from its carrier`);
    }
  }
}

function relianceAccepts(satisfaction, complete, outcomes) {
  if (!Array.isArray(outcomes) || outcomes.length === 0
      || satisfaction !== 'SATISFIED' || complete !== true) {
    return 'reject';
  }
  return outcomes.every((outcome) => outcome === 'success') ? 'accept' : 'reject';
}

function schemaCases() {
  const schemaFixture = JSON.parse(fs.readFileSync(SCHEMA_FIXTURE, 'utf8'));
  const subject = bindingSubject(schemaFixture.binding);
  printCase('EMI-BIND-011', 'schema-bearing set has a new subject',
    schemaFixture.expected_subject, subject);
  for (const testCase of schemaFixture.schema_cases) {
    const binding = JSON.parse(JSON.stringify(schemaFixture.binding));
    const results = JSON.parse(JSON.stringify(schemaFixture.native_status_results));
    const mutation = testCase.mutation;
    if (mutation === 'none') {
      // no change
    } else if (mutation === 'missing') {
      delete binding.targets[0].status_schema;
    } else if (mutation === 'unpinned') {
      binding.targets[0].status_schema.digest = 'sha-256:' + '0'.repeat(64);
    } else if (mutation === 'schema-mismatch') {
      results[0].status_schema.id = 'https://emiliaprotocol.ai/schemas/other-status-v1.json';
    } else if (mutation === 'omitted') {
      results.push({
        artifact_id: 'approval-carol',
        status_schema: {
          id: 'https://emiliaprotocol.ai/schemas/ep-quorum-status-v1.json',
          version: '1',
          digest: 'sha-256:' + '0'.repeat(64),
        },
      });
    } else {
      throw new Error(`unknown schema mutation ${mutation}`);
    }
    let got = 'accept';
    try {
      schemaCarrierError(schemaFixture, binding, results);
    } catch {
      got = 'reject';
    }
    printCase(testCase.id, testCase.name, testCase.expected, got);
  }
  for (const testCase of schemaFixture.completeness_cases) {
    const got = relianceAccepts(
      testCase.satisfaction, testCase.complete, testCase.required_outcomes,
    );
    printCase(testCase.id, testCase.name, testCase.expected, got);
  }
}

const fixture = JSON.parse(fs.readFileSync(FIXTURE, 'utf8'));
if (digestObject(fixture.binding.trust_inputs) !== fixture.binding.trust_snapshot_digest) {
  throw new Error('trust_snapshot_digest does not match trust_inputs');
}
const subject = bindingSubject(fixture.binding);
const bindingRole = fixture.binding_role;
{
  const required = fixture.source_requirement.required_bindings[0];
  if (bindingRoleName(required.from_type, required.relation, required.to_type)
      !== bindingRole) throw new Error('required binding role drifted');
  const endpoints = fixture.binding;
  if (bindingRoleName(
    endpoints.source.type, endpoints.relation, endpoints.targets[0].type,
  ) !== bindingRole) throw new Error('binding tuple endpoints drifted');
}

console.log('EMILIA → CLC evidence projection probe (TypeScript)');
console.log('fixture: register/cmd/emilia-projection-probe/testdata/'
  + 'emilia-binding-fixture-v1.json');
console.log();

{
  const source = fixture.source_requirement;
  const projected = projectAec(source);
  const expected = fixture.mapped_requirement;
  printCase('EMI-PROJ-001', 'AEC projects to the pinned CLC requirement',
    'match',
    clc.canonicalJSON(projected) === clc.canonicalJSON(expected)
      ? 'match' : 'different');
  printCase('EMI-PROJ-002', 'source requirement digest',
    fixture.requirement_digests.source, requirementDigest(source));
  printCase('EMI-PROJ-003', 'projected requirement digest',
    fixture.requirement_digests.projected, requirementDigest(projected));
}

{
  const negativeSource = fixture.source_requirement;
  const negative = [
    ['EMI-PROJ-004', 'unknown AEC member rejected',
      (doc) => { doc.authorized = true; }],
    ['EMI-PROJ-005', 'unpinned role rejected',
      (doc) => { doc.freshness_sec = { unpinned: 30 }; }],
    ['EMI-PROJ-006', 'over-long projected expression rejected',
      (doc) => { doc.expression = 'a'.repeat(520); }],
    ['EMI-PROJ-007', 'unknown role constraint rejected',
      (doc) => { doc.role_constraints[0].type = 'new-constraint'; }],
    ['EMI-PROJ-008', 'presenter-supplied subject rejected',
      (doc) => { doc.role_constraints[0].subject_id_source = 'presenter'; }],
    ['EMI-PROJ-009', 'empty binding part rejected',
      (doc) => { doc.required_bindings[0].from_type = ''; }],
    ['EMI-PROJ-010', 'quorum below two rejected',
      (doc) => { doc.role_constraints[0].threshold = 1; }],
    ['EMI-PROJ-011', 'invalid expression grammar rejected',
      (doc) => { doc.expression = 'ep-quorum AND'; }],
    ['EMI-PROJ-012', 'unknown nested role-constraint member rejected',
      (doc) => { doc.role_constraints[0].note = 'x'; }],
    ['EMI-PROJ-013', 'negative freshness rejected',
      (doc) => { doc.freshness_sec['ep-quorum'] = -1; }],
    ['EMI-PROJ-014', 'unknown AEC version rejected',
      (doc) => { doc['@version'] = 'EP-AEC-REQUIREMENT-v2'; }],
    ['EMI-PROJ-015', 'missing requirement id rejected',
      (doc) => { delete doc.requirement_id; }],
    ['EMI-PROJ-016', 'invalid binding identifier rejected',
      (doc) => { doc.required_bindings[0].from_type = 'policy permit'; }],
    ['EMI-PROJ-017', 'over-long binding role rejected',
      (doc) => { doc.required_bindings[0].from_type = 'a'.repeat(200); }],
    ['EMI-PROJ-018', 'unknown nested binding member rejected',
      (doc) => { doc.required_bindings[0].note = 'x'; }],
    ['EMI-PROJ-019', 'unpinned status_required role rejected',
      (doc) => { doc.status_required = ['unpinned']; }],
  ];
  for (const [id, name, mutate] of negative) {
    const candidate = JSON.parse(JSON.stringify(negativeSource));
    mutate(candidate);
    let got = 'rejected';
    try {
      const projected = projectAec(candidate);
      evidence.evaluateRequirement(projected, [], { now: fixture.now });
      got = 'accepted';
    } catch {
      // expected
    }
    printCase(id, name, 'rejected', got);
  }
}

printCase('EMI-BIND-001', 'base relation tuple has the pinned subject',
  fixture.expected_subject, subject);

const reversedBinding = { ...fixture.binding, targets: [...fixture.binding.targets].reverse() };
printCase('EMI-BIND-007',
  'artifact set order does not change the relation subject',
  'unchanged',
  bindingSubject(reversedBinding) === subject ? 'unchanged' : 'different');

let duplicateVerdict = 'accepted';
try {
  canonicalArtifactSet([...fixture.binding.targets, fixture.binding.targets[0]]);
} catch {
  duplicateVerdict = 'rejected';
}
printCase('EMI-BIND-008', 'duplicate artifact member rejected',
  'rejected', duplicateVerdict);

let mixedVerdict = 'accepted';
try {
  const mixed = fixture.binding.targets.map((target) => ({ ...target }));
  mixed[mixed.length - 1].type = 'policy-permit';
  canonicalArtifactSet(mixed);
} catch {
  mixedVerdict = 'rejected';
}
printCase('EMI-BIND-009', 'mixed target types rejected', 'rejected', mixedVerdict);

let emptyVerdict = 'accepted';
try {
  canonicalArtifactSet([]);
} catch {
  emptyVerdict = 'rejected';
}
printCase('EMI-BIND-010', 'empty artifact set rejected', 'rejected', emptyVerdict);

schemaCases();

for (const testCase of fixture.evidence_cases) {
  const [verdict, reason] = evidence.evaluateRequirement(
    fixture.mapped_requirement,
    evidenceFacts(testCase, fixture.now, subject),
    { now: fixture.now },
  );
  printCase(testCase.id, testCase.name, testCase.expected_got,
    verdictString(verdict, reason));
}

const caid = fixture.caid;
const operationId = clc.computeActionID(
  caid.type.name, caid.type.material, caid.suite, caid.operation,
);
for (const testCase of caid.cases) {
  const observedId = clc.computeActionID(
    caid.type.name, caid.type.material, caid.suite, testCase.observed,
  );
  const got = operationId === observedId ? 'MATCH' : 'NOT_EQUIVALENT';
  printCase(testCase.id, testCase.name, testCase.want, got);
}

const bindingIds = {
  source: 'EMI-BIND-002',
  target: 'EMI-BIND-003',
  action: 'EMI-BIND-004',
  status: 'EMI-BIND-005',
};
for (const kind of Object.keys(bindingIds)) {
  const changed = bindingSubject(mutate(fixture.binding, fixture.mutations[kind]));
  printCase(bindingIds[kind], `${kind} mutation changes the relation subject`,
    'different', changed === subject ? 'unchanged' : 'different');
}

const opaqueCase = {
  facts: {
    'ep-quorum': [
      { subject: 'alice', verified: true, age_sec: 30 },
      { subject: 'bob', verified: true, age_sec: 20 },
    ],
    'policy-permit': [{ subject: 'policy', verified: true, age_sec: 60 }],
    [bindingRole]: [
      { subject: 'arbitrary-unbound-subject', verified: true, age_sec: 60 },
    ],
  },
};
const [opaqueVerdict, opaqueReason] = evidence.evaluateRequirement(
  fixture.mapped_requirement,
  evidenceFacts(opaqueCase, fixture.now, subject),
  { now: fixture.now },
);
printCase('EMI-BIND-006', 'CLC treats the binding subject as opaque',
  'opaque-subject-accepted',
  verdictString(opaqueVerdict, opaqueReason) === 'SATISFIED'
    ? 'opaque-subject-accepted' : 'unexpectedly-rejected');
