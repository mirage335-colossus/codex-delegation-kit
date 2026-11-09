import sys, torch
sys.path.insert(0, '/tmp/pump-review-baseline28/tools')
from triad_gaussian_state import GaussianPrior, GaussianStateFilter
torch.set_num_threads(1)
v=torch.tensor([[1.,1.],[1.,1.]],dtype=torch.float32)
# Construct two nearly identical but independently quantized columns from deterministic inputs.
for eps in (2**-10, 2**-12, 2**-14):
    basis=torch.tensor([[1.,1.],[1.,1.+eps],[0.,0.]],dtype=torch.float64)
    q=basis.to(torch.float32)
    g32=(q.mT@q).to(torch.complex64).to(torch.complex128)
    g64=q.to(torch.float64).mT@q.to(torch.float64)
    g64=g64.to(torch.complex128)
    filt=GaussianStateFilter(GaussianPrior((1.,1.)),dtype=torch.complex128)
    filt._largest_relative_gram_repair=torch.zeros((),dtype=torch.float64)
    results=[]
    for name,g in [('fp32_gram_cast',g32),('fp64_gram_quantized_basis',g64)]:
        try:
            filt._validate_gram(g)
            outcome='pass'
        except Exception as ex:
            outcome=f'{type(ex).__name__}: {ex}'
        eig=torch.linalg.eigvalsh((g+g.mH)*.5).tolist()
        results.append((name,outcome,eig))
    print('eps',eps,'basis_dtype',q.dtype,'gram_shapes',tuple(g32.shape),tuple(g64.shape),'results',results)
