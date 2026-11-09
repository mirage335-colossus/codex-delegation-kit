"""One bounded acquisition-stage probe on a simplified case-derived HF waveform.

This is diagnostic only: 2 s source, one public epoch/clock/frequency, flat high
SNR channel and known source start to +/-0.2s. No tracking or admission claim.
"""
import json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path('tools').resolve()))
import numpy as np
from triad_continuous import NativeStream
from triad_realtime_fft import FFTScreen

bit=int(sys.argv[1]) if len(sys.argv)>1 else 0
if bit not in (0,1):raise ValueError('expected bit 0 or 1')
scenario=sys.argv[2] if len(sys.argv)>2 else 'flat'
if scenario not in ('flat','hf-worst'):raise ValueError('expected flat or hf-worst')
fs=6000
args=['--case','hf','--sample-rate',str(fs),'--rate','36','--added-symbols','10','--fhss','off','--seconds','45','--key-seed','95031','--epoch','1793850000','--helper','off','--spread-preset','none','--selective-perturbation','off','--oscillator-effects','off','--control','flat','--arrival-seconds','0','--cn0','80','--bit',str(bit)]
if scenario=='hf-worst':
 args[args.index('--spread-preset')+1]='hf-worst'
 args[args.index('--selective-perturbation')+1]='each-65'
 args[args.index('--control')+1]='selected'
s=NativeStream('build/witness/triad_helper_export',args,kind='channel')
try:
 d=s.descriptor; physics=s.plan['physics']
 # Sender truth is used only to place the intentionally reduced diagnostic window;
 # hypotheses still include both bits and a +/-0.2 second arrival interval.
 first=45*fs; n=4*fs; parts=[]
 while s.next_sample<first+n:
  position=s.next_sample
  samples,valid=s.next(min(16384,first+n-position))
  if not valid.all():raise RuntimeError('erasure in diagnostic slice')
  if position+len(samples)>first:parts.append(samples[max(0,first-position):])
 raw=np.concatenate(parts)
 samples=s.basis(0,2*fs,[(b,0,0,0,0,0,0) for b in (0,1)])
finally:s.close()
assert raw.size==n
expected_start=(d['data_offset_samples']+round(d['capture_lead_seconds']*fs)-first)/fs
manifest={'sample_rate_hz':fs,'calendar':{'capture_samples':len(raw),'capture_lead_seconds':0.,'data_sample_offset':round(expected_start*fs),'arrival_prior_seconds':[-.2,.2]},'channel':{'spread_delay_ms':physics['spread_delay_ms'],'spread_doppler_hz':physics['spread_doppler_hz']},'format':{'occupied_bandwidth_hz':225.,'fine_chip_rate_hz':60.},'power':{'complex_noise_variance':d['noise_variance']}}
templates=samples.reshape(1,2,-1)
prepare=time.perf_counter(); screen=FFTScreen(manifest,templates,[0],clock_ppm=(0.,),workers=1,precision='fp32');prep=time.perf_counter()-prepare
start=time.perf_counter();result=screen.score(raw,frequencies_hz=[0.],top_per_bit=1);elapsed=time.perf_counter()-start
rows=result.get('candidates',[])
print(json.dumps({'scope':'case-derived HF, 2 s acquisition screen, reduced search; no fine search or tracking','scenario':scenario,'channel':manifest['channel'],'input_rate':fs,'template_shape':templates.shape,'preparation_wall_s':prep,'screen_wall_s':elapsed,'status':result.get('status'),'reason':result.get('reason'),'candidates':rows,'source_bit':bit,'expected_arrival_relative_to_manifest_s':0.},indent=2))
if len(rows)!=2:raise SystemExit('expected a candidate for both bits')
winner=max(rows,key=lambda r:r['score'])
if winner['bit'] != bit or abs(winner['arrival']) > .005:raise SystemExit('bit or arrival mismatch')
