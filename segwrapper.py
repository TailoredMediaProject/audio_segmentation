from inaSpeechSegmenter import Segmenter
from inaSpeechSegmenter.export_funcs import seg2csv, seg2textgrid
from segwrapper import merge_visualise

import subprocess
import os

import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

def ina_segmenter(media,outfile):

    seg = Segmenter()

    segmentation = seg(media)
    
    seg2csv(segmentation, outfile)
    
def lium_segmenter(media,outfile):

    liumdir = '/lium'
    
    subprocess.run(['ffmpeg','-i',media,liumdir+'/tmp.wav'], capture_output=True)
    
    subprocess.run(['java','-Xmx2024m','-jar','./LIUM_SpkDiarization-8.4.1.jar','--fInputMask='+liumdir+'/tmp.wav','--sOutputMask='+outfile,'--doCEClustering','tmp'],cwd=liumdir,capture_output=True)
    
    
def merge_plot(media,outdir,inafile,liumfile,params=None,timerange=None):
    
    if params==None:
        params = get_default_params()
    
    ina_df = merge_visualise.parse_ina(inafile)
	 
    lium_df = merge_visualise.parse_lium(liumfile)
	 	
    merged_df = merge_visualise.merge_ina_lium(ina_df,lium_df)
	
    merged_df = merge_visualise.group_segments(merged_df,params)

    merged_df = merge_visualise.classify_segments(merged_df,params)

    mediabasename = '.'.join(media.split('.')[:-2])
    mediabasename = media.split('/')[-1]
    
    merge_visualise.plot(merged_df,os.path.join(outdir,mediabasename+'_plot_merged.png'),timerange)
    merge_visualise.plot(merged_df,os.path.join(outdir,mediabasename+'_plot_merged_speakers.png'),timerange,['speakers'])
   
    merge_visualise.plot(merged_df,os.path.join(outdir,mediabasename+'_plot_merged_groups.png'),timerange,['groups'])
  
    merge_visualise.plot(merged_df,os.path.join(outdir,mediabasename+'_plot_merged_group_cls.png'),timerange,['groupclasses'])

    
def segment_plot(media,outdir,params=None,timerange=None):
    mediabasename = '.'.join(media.split('.')[:-2])
    mediabasename = media.split('/')[-1]
    
    inafn = os.path.join(outdir,mediabasename+'_ina.csv')
    liumfn = os.path.join(outdir,mediabasename+'_lium.csv')   
    
    ina_segmenter(media,inafn)
    lium_segmenter(media,liumfn)
    
    merge_plot(media,outdir,inafn,liumfn,params=params,timerange=timerange)
    
def get_default_params():
    
    params = {}
    params['song_min_dur'] = 30
    params['grp_speaker_pause'] = 120
    params['grp_min_dur'] = 30
    
    sth = {}
    params['score_thresholds'] = sth
    sth['music_p'] = {}
    sth['music_p']['music_min'] = 0.7
    sth['music_p']['hosted_max'] = 0.5
    sth['music_h'] = {}
    sth['music_h']['music_min'] = 0.1
    sth['music_h']['hosted_min'] = 0.5
    sth['info_h'] = {}
    sth['info_h']['music_max'] = 0.1
    sth['info_h']['hosted_min'] = 0.5
    sth['info_h']['info_min'] = 0.5
    sth['talk_h'] = {}
    sth['talk_h']['music_max'] = 0.1
    sth['talk_h']['hosted_min'] = 0.5
    sth['talk_h']['info_max'] = 0.5    
    sth['talk/info'] = {}
    sth['talk/info']['music_max'] = 0.1
    sth['talk/info']['hosted_max'] = 0.5
    sth['talk/info']['info_min'] = 0.5   
    sth['ad'] = {}
    sth['ad']['ad_min'] = 0.5
    sth['ad']['music_max'] = 0.1
    sth['ad']['hosted_max'] = 0.4   
    
    return params

def print_params(params,indentation=0):
    for k,v in params.items():
        indstr = ''
        for i in range(indentation):
            indstr = indstr + '  '
        if isinstance(v, dict):
            print(indstr+k)
            print_params(v,indentation+1)
        else:
            print(indstr+str(k)+' '+str(v)) 