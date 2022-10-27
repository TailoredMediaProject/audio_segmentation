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
    
    
def merge_plot(media,outdir,inafile,liumfile,timerange=None):
    
    params = {}
    params['song_min_dur'] = 30
    params['grp_speaker_pause'] = 120
    params['grp_min_dur'] = 30
    
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

    
def segment_plot(media,outdir):
    mediabasename = '.'.join(media.split('.')[:-2])
    mediabasename = media.split('/')[-1]
    
    inafn = os.path.join(outdir,mediabasename+'_ina.csv')
    liumfn = os.path.join(outdir,mediabasename+'_lium.csv')   
    
    ina_segmenter(media,inafn)
    lium_segmenter(media,liumfn)
    
    merge_plot(media,outdir,inafn,liumfn)