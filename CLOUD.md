# Cloud experiment guide

Use cloud compute only when a specific experiment is likely to finish sooner
end to end. Under the user's standing authorization, use RunPod and Linode
proactively for suitable experiments within the limits below. Preserve each
task's scope, permissions, holds, model, owner, and acceptance criteria; do
not seek fresh human approval for compute already covered by this standing
authorization. The assigned operator launches or extends only after completing
the budget gate below. The operator may promptly delete resources they own or
are otherwise authorized to manage, and reconcile costs, even while usage is
uncertain; no extra spend approval is needed to stop or delete authorized
resources. Do not delete resources outside that authority. Advice alone does
not authorize operations outside the standing scope or override normal
service permissions. Current provider terms, capabilities, and prices can
change; check official provider documentation and the selected account's
current controls before launch.

**GPU default: evaluate and prefer RTX PRO 6000 Blackwell for suitable tensor
and highly parallel FP32 numerical work, compatibility/utilization demonstrations,
and accelerated testing.** Do not default to A100, RTX A5000 or another older
GPU without a concrete reason. Before selecting a device, apply the policy's
[GPU selection and performance evidence](policy.md#gpu-selection-and-performance-evidence)
criteria for exact variant (including unverified "WX" labels), FP64 and other
workload exceptions, software support, and measured end-to-end gains. Existing
budget and launch controls below still apply.

For compute-intensive paths in native applications, follow the policy's
[native numerical processing preference](policy.md#native-numerical-processing).
Prefer a reproducible native executable or benchmark target exercising the
actual application code for RunPod and other GPU tests. Account for dependencies,
setup, transfers and end-to-end execution before introducing separate Python
processing scripts; Python orchestration can still launch the native target.
Build the minimal native source closure and extend production CPU/GPU interfaces
instead of creating a second DSP implementation for easier deployment. Fresh
native test processes are valid isolation, not a split operating chain. Keep
source/workload identities attached to measurements; GPU speed alone does not
qualify a CPU forecast or sustained receiver capacity.

## Cloud workload integrity and security

After a suspected incident, use a fresh, trusted image and clean storage. Send
only the code and data the experiment needs. Avoid sending API credentials or
SSH private keys to pods; when a workload needs a credential, use RunPod secret
references rather than literal template values and remove access when finished.
For SSH, verify host keys and disable agent forwarding. Expose only the ports
the experiment needs, and protect any required public service. If a credential
may have reached a compromised pod, promptly revoke or rotate it with its
issuing provider and preserve useful evidence privately. Treat results from a potentially
compromised host as untrusted: independently check important outputs and never
execute suspect downloads on a trusted machine. These steps reduce exposure;
they cannot protect a workload from a malicious provider host.

## Decide whether cloud helps

Identify the actual expensive path in this source revision: for example, a
slow helper, a headless component, an independent case batch, or a portable
benchmark. Name the expected bottleneck and the result that would distinguish
the leading explanations. A generic request for a faster GPU is not a proposal.

Propose the smallest faithful, runnable slice that exercises that path. Name
the original inputs and assertions, required dependencies and data, any needed
adapter change and its assertions, and the proposed CPU, GPU, memory, storage,
and toolchain. Preserve the original failing comparison and input identity,
coverage, assignment ownership, repair limits, and acceptance route. Estimate
total turnaround before building the adapter: include adaptation, provisioning,
queueing, data transfer, build, execution, result retrieval, and cleanup. Use
ranges for uncertainty, state assumptions, and identify a cheap useful test
that could falsify the proposal. Reuse authorized capacity, cached data, and
results first. Avoid building a remote platform for one experiment. Implement
the adapter only when the estimate shows a credible, meaningful total-time gain
or a cheap useful falsifying test justifies it. Otherwise stay local; local
evidence collection can continue without cloud spending. When implemented, the
slice must answer the same question as the local run. A cloud result does not
qualify throughput on intended end-user hardware. Existing permitted experts
may advise on cloud experiments; Terra may screen evidence, Luna may scout
facts or implement a settled adapter, and Sol/Astra architecture gates remain
unchanged. Do not add an expert turn by default or nest more agents.

## Advice and launch authority

Cloud advice is not launch authority. The existing permitted operator owns
launch, extensions, and cleanup under the task's authorization. This guide is
generic: do not add account addresses, balances, resource IDs, inventories,
status, billing records, provider logs, caches, or cleanup receipts to it.
Verify current official provider documentation and account controls at launch;
the links below describe relevant billing and deletion behavior, not a spend
cap or guarantee of cleanup.

All user limits apply across all chats, hosts, and resources. For each provider,
incurred usage must stay strictly below USD 100 per calendar day in
America/Chicago. Separately, combined incurred usage across providers must
stay strictly below USD 200 per calendar day; the provider limits are not
pooled. Include compute, storage, backups, applicable transfer, and taxes.
Deposits and funding are not usage and must not be counted twice.

Before launch or extension, reconcile existing usage, active resources, and
delayed or unsettled costs. Bound maximum additional cost through cleanup,
including rounding, billing delay, taxes, and a margin. Allocate that bound
across Chicago calendar-day boundaries, including daylight-saving changes;
midnight does not erase commitments already running. Cross-host budget
reservations are usually unnecessary. When concurrent activity presents a
concrete risk of exceeding a shared limit, make a proportionate best effort
to coordinate, using an existing shared mechanism if readily available. A
host-local lock does not coordinate other hosts. Do not make a shared
reservation service a prerequisite or ask the user to supply one merely
because it is unavailable. Account for known commitments through deletion
and cost reconciliation. Lack of a shared reservation service or complete
cross-host visibility alone does not establish unknown or unbounded exposure.
Unknown or unbounded exposure blocks new spending, while independent
investigation can continue. This guide is not implemented billing enforcement,
a controller, or a provider spend cap.

For Linode, keep aggregate spend strictly below USD 10 per hour and set a
concrete deadline of a few hours or less before launch. Promptly delete
experimental instances and leftovers. For RunPod, target aggregate spend below
USD 10 per hour; a higher rate is acceptable only for a bounded run that fits
the remaining daily limits and margin. Release idle compute promptly. Keep
network cache volumes only for a justified time gain. Account for their ongoing
cost, set a concrete review or expiry date, and retain an owner through that
review or expiry. Use lightweight notes where useful; a separate bookkeeping
system is not required.

Use an available authenticated provider browser console for launch, monitoring,
and cleanup when that is the practical route. If readily available and useful,
make a best effort to arrange independent cleanup through an authorized provider
termination or external control plane. Do not make separate API credentials,
an independently authenticated mechanism, automation, or a bookkeeping system
a prerequisite; do not ask the user for a credential or its location solely to
set one up. Use the browser directly when that is what is available. Do not rely
on VM self-shutdown or credit exhaustion. Verify deletion in the provider
control plane, including persistent volumes, backups, IPs, and other billable
resources; stopping compute does not prove charges ended. If cleanup fails,
retain the owner, account for continuing liability including any reservation
in use, and report the failure. Do not extend implicitly. Do not enable AutoPay,
raise account limits, or purchase credits.

Provider documentation describes why cleanup must cover related resources:
[RunPod Pod pricing](https://docs.runpod.io/pods/pricing) and [network volume
pricing](https://docs.runpod.io/storage/network-volumes) describe continuing
storage charges; [RunPod pod removal](https://docs.runpod.io/runpodctl/reference/runpodctl-remove-pods)
documents pod stop/termination behavior. Check the current supported interface
and options before using it. [Linode billing](https://techdocs.akamai.com/cloud-computing/docs/understanding-how-billing-works)
describes billing behavior, while [deleting a Linode
instance](https://techdocs.akamai.com/linode-api/reference/delete-linode-instance)
can leave separately billed volumes or other resources. The [volume deletion
API](https://techdocs.akamai.com/linode-api/reference/delete-volume) documents
volume removal; inspect and release reserved IPs separately through the
current provider interface.
Verify current rounding, plan terms, transfer charges, and taxes at launch.

## Keep operational records private

Account-specific resource IDs, inventories, status, account addresses,
balances, billing or spend records, provider logs, caches, and cleanup receipts
must live outside every development repository, including ignored and
untracked files and generated outputs. Put chat- or account-wide shared
operational state outside the checkout from its first creation. This includes
the operations working directory, temporary paths, logs, and cache paths.
Never run a provider CLI in a repository on the assumption that `.gitignore`
or later redaction makes the data safe. Keep only generic reusable guidance
or tooling in the repository; sanitized technical experiment results may be
recorded without provider account metadata.

In native-only coordination, preserve assignment identity, engineering
bookkeeping, failures, ownership, decisions, and acceptance evidence in native
history; do not create engineering assignment registries, ledgers, or reports.
Any financial and resource-control state kept for cloud operations is separate
and must be maintained outside the repository. Repository
helpers or controller receipt stores must not capture cloud account operations
data. Use a permitted private operational route without bypassing task
authorization or the selected controller boundary.
