import pandas as pd
import os

import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

def parse_ina_row(row):

    row['type'] = row['labels']
    row['gender'] = 'X'
    if row['labels']=='male': 
        row['gender'] = 'M'
        row['type'] = 'speech'
    if row['labels']=='female': 
        row['gender'] = 'F'
        row['type'] = 'speech'	
		
    if row['labels']=='noEnergy': row['type'] = 'silence'

    row['speech_type'] = 'X'
    row['speaker_id'] = ''
    row['channel'] = '-1'

	
    return row

	
def parse_lium_row(row):

    row['type'] = 'speech'

    row['stop'] = int(row['start'])+int(row['length'])
	
    row['start'] = row['start']/100.0
    row['stop'] = row['stop']/100.0
	
    return row
	
def parse_aalto_row(row):

    row['type'] = 'speech'

    row['start'] = float(row['start'].split('=')[-1])
    row['stop'] = float(row['stop'].split('=')[-1])
    row['speaker_id'] = row['speaker_id'].split('=')[-1]
	
    row['speech_type'] = 'X'
    row['channel'] = '-1'
    row['gender'] = 'X'
	
    return row
	
def parse_ina(filename):

    ina_df = pd.read_csv(filename, sep='\t')
  
    ina_df = ina_df.apply(lambda r: parse_ina_row(r), axis=1 ) 

    ina_df = ina_df.drop('labels', axis=1)
	
    return ina_df
	
	
def parse_lium(filename):

    lium_df = pd.read_csv(filename, sep=' ', comment=';', header=None)
    lium_df = lium_df.set_axis(['file','channel','start','length','gender','speech_type','env','speaker_id'], axis=1)
  
    lium_df = lium_df.apply(lambda r: parse_lium_row(r), axis=1 ) 

    lium_df = lium_df.drop('file', axis=1)
    lium_df = lium_df.drop('length', axis=1)
    lium_df = lium_df.drop('env', axis=1)

	
    return lium_df
	
def parse_aalto(filename):

    aalto_df = pd.read_csv(filename, sep=' ', header=None)
    aalto_df = aalto_df.set_axis(['file','lna','start','stop','speaker_id'], axis=1)
  
    aalto_df = aalto_df.apply(lambda r: parse_aalto_row(r), axis=1 ) 

    aalto_df = aalto_df.drop('file', axis=1)
    aalto_df = aalto_df.drop('lna', axis=1)
    	
    return aalto_df
	


def merge_ina_lium(ina_df,lium_df):

    # keep LIUM speech segments
    df = lium_df.copy(deep=True)
	
    # check gender mismatch
    for index, row in df.iterrows():
        overlapping = ina_df.loc[(ina_df['start'] <= row['start']) & (ina_df['stop'] >= row['stop'])]
	
        if len(overlapping)==0: continue

        for index2, row2 in overlapping.iterrows():
            if row2['type'] != 'speech': continue
			
            if row2['gender'] != 'X':
                if row['gender'] == 'X':
                    df.at[index,'gender'] = row2['gender']
                elif row2['gender'] != row['gender']: 
                    df.at[index,'gender'] = 'C'
	
	# add INA music & noise
    
    for index, row in ina_df.iterrows():
        if (row['type'] == 'music') or (row['type'] == 'noise'):
            df = df.append(row)

    return df			
	
	
def det_jingle(r,jingledur):
    
    if r['type'] != 'music': return r
	
    if r['stop']-r['start']<=jingledur:
        r['type'] = 'jingle'
		
    return r
	
	
def group_segments(df,params):

    df['group_id'] = ''
	
    df = df.sort_values('start', axis=0)
    df = df.reset_index(drop=True)

    # classify jingles vs music
    jingledur = params['song_min_dur']
	
    df = df.apply(lambda r: det_jingle(r,jingledur), axis=1 ) 

    grp_min_dur = params['grp_min_dur']
    grp_speaker_pause = params['grp_speaker_pause']
		
    last_end = None
    grp_id = 0
	
    # remove speech overlapping with songs
    #for index, row in df.iterrows():
    #    overlapping = df.loc[(df['start'] <= row['start']) & (df['stop'] >= row['stop'])]
	#
    #    if len(overlapping)==0: continue

    #    for index2, row2 in overlapping.iterrows():
    #        if row2['type'] == 'music':
    #            df.at[index,'type'] = 'music'
    
	
    # dict with key=type of speaker id, values = (end time, indices, grp_id)
    active_segments = {}
	

	
    for index, row in df.iterrows():

        if last_end == None:
            last_end = row['start']

        # check if segment should be merged with previous
        found_seg = False
        mykey = row['type']
        if row['type'] == 'speech': 
            mykey = row['speaker_id']
        myaltkey = mykey + '_' +str(index)
        for a in active_segments:
            akey = a.split('_')[0]

            if akey == mykey:
                if row['type'] != 'speech':

                    if row['start']-active_segments[a][0] > grp_min_dur:
                     
                        continue
                else:
                    if row['start']-active_segments[a][0] > grp_speaker_pause:
                        continue
						
                found_seg = True
						
                idxlist = active_segments[a][1]
                idxlist.append(index)
                active_segments[a] = (row['stop'], idxlist, active_segments[a][2])
                last_end = max(last_end, row['stop'])

					
        # add newly found segment, if overlapping
        if not(found_seg):
            mykey = myaltkey
		
            if row['start']>=last_end:
			
                # new segment
                grp_id += 1
				
                segdata = (row['stop'],[index], grp_id)
                active_segments[mykey] = segdata
                last_end = max(last_end, row['stop'])

	
            else: 
                segdata = (row['stop'],[index], grp_id)
                active_segments[mykey] = segdata
                last_end = max(last_end, row['stop'])
	
				
	    # check if past active segment shall be merged or added
        lastprevgrp = {}
        for a in active_segments:
            if active_segments[a][2] in lastprevgrp:
                lastprevgrp[active_segments[a][2]] = max(active_segments[a][0],lastprevgrp[active_segments[a][2]])
            else:
                lastprevgrp[active_segments[a][2]] = active_segments[a][0]            

        # check if last of one group is later than that of group with lower id,
		# or if outdated group is too short
        merge = []
        for l1 in lastprevgrp:
            for l2 in lastprevgrp:
                if l1==l2: continue
                if (l1<l2) and (lastprevgrp[l1]>lastprevgrp[l2]):
                    merge.append((l1,l2))
                if row['start'] > lastprevgrp[l1] + max(grp_min_dur,grp_speaker_pause):
                    grpstart = 999999999999
                    grpstop = -1

                    for a in active_segments:
                        if active_segments[a][2] == l1:
                            for i in active_segments[a][1]:
                                grpstart = min(grpstart,df.at[i,'start'])
                                grpstop = max(grpstop,df.at[i,'stop'])


                    if grpstop - grpstart < grp_min_dur:
                        merge.append((l1,l2))

				
        if len(merge)>0:
            for m in merge:
                for a in active_segments:
                    if active_segments[a][2] == m[0]:
                        active_segments[a] = (active_segments[a][0],active_segments[a][1],m[1])
					
        # check if segment data can be written to table
        writeToTable = []
        
       
        for l in lastprevgrp:
          
            if row['start'] > lastprevgrp[l] + max(grp_min_dur,grp_speaker_pause):
                writeToTable.append(l)
 
        for l in writeToTable:
            remainingSegments = {}		

            for a in active_segments:
                if active_segments[a][2] == l:            
                    for i in active_segments[a][1]:
                        df.at[i,'group_id'] = active_segments[a][2]

                else:
                    remainingSegments[a] = active_segments[a]
            active_segments = remainingSegments		

    # write remaining groups
    for l in lastprevgrp:
        remainingSegments = {}		

        for a in active_segments:
            if active_segments[a][2] == l:            
                for i in active_segments[a][1]:
                    df.at[i,'group_id'] = active_segments[a][2]

            else:
                remainingSegments[a] = active_segments[a]
        active_segments = remainingSegments		
            
    return df
	

def classify_segments(df,params):

    df['group_cls'] = '()'

    grpids = df['group_id'].unique().tolist()
    
    for g in grpids:
        grpmembers = df.loc[df['group_id'] == g]
	
        speaker_durations = {}
        total_speaker_duration = 0
        music_duration = 0
        jingle_duration = 0
        duration = 0
	
        for index, row in grpmembers.iterrows():        


            if row['type']=='speech':
                if row['speaker_id'] in speaker_durations.keys():
                    speaker_durations[row['speaker_id']] += row['stop']-row['start']
                else:
                    speaker_durations[row['speaker_id']] = row['stop']-row['start']
                total_speaker_duration += row['stop']-row['start']
            elif row['type'] == 'jingle':
                jingle_duration += row['stop']-row['start']
            elif row['type'] == 'music':
                music_duration += row['stop']-row['start']
				
            duration += row['stop']-row['start'] 
	
        music_frac = music_duration / duration
        jingle_frac = jingle_duration / duration
        speaker_frac = total_speaker_duration / duration
			
        nspeakers = len(speaker_durations.keys())
        speakers_permin = 60*nspeakers/duration
			
        longest_speaker = 0
        for d in speaker_durations:
            if speaker_durations[d]>longest_speaker:
                longest_speaker = speaker_durations[d]
					
        longest_speaker_frac = 0
        if total_speaker_duration>0:
            longest_speaker_frac = longest_speaker / total_speaker_duration
		
        hosted_score = longest_speaker_frac
        music_score = music_frac
        ad_score = 0.3*(min(2,speakers_permin)-2) + jingle_frac + 1- hosted_score 
        if speakers_permin>=1:
            info_score = 0.3/min(3,speakers_permin) + jingle_frac + hosted_score
        else:
            info_score = 0
		
        print(g,hosted_score,music_score,ad_score,info_score)		

        cls = 'unknown'
        if music_score>0.7 and hosted_score<0.5:
            cls = 'music_p'
        if hosted_score>0.5 and music_score>0.1:
            cls = 'music_h'
        if hosted_score>0.5 and info_score>0.5 and music_score<0.1:
            cls = 'info_h'
        if hosted_score>0.5 and info_score<0.5 and music_score<0.1:
            cls = 'talk_h'
        if hosted_score<0.5 and info_score>0.5 and music_score<0.1:
            cls = 'talk/info'
        if ad_score>0.5 and music_score<0.1 and hosted_score<0.4:
            cls = 'ad'		

        for index, row in grpmembers.iterrows():        
			
            df.at[index,'group_cls'] = cls			

    return df
	
def plot(df,fn,timerange=None,specific=None):

    # check for specific categories to plot
    speakers = False
    groups = False
    groupclasses = False
    if specific is not None:
        if 'speakers' in specific:
            speakers = True
        if 'groups' in specific:
            groups = True
        if 'groupclasses' in specific:
            groupclasses = True			
    data = []

    groupdata = {}
	
    for index, row in df.iterrows():
        t = row['type']
        if t=='silence': continue	

        if timerange is not None:
            if int(row['start'])>=timerange[1]: continue
            if int(row['stop'])<=timerange[0]: continue
 
        if t=='speech':
            gend = row['gender']
            if gend=='X': gend='C'
            t = t + ' ' + gend
            if speakers:
                t = row['speaker_id']

        if groups:
            if row['group_id'] in groupdata.keys():
                groupdata[row['group_id']] = (min(groupdata[row['group_id']][0],row['start']), max(groupdata[row['group_id']][1],row['stop']))
            else:
                groupdata[row['group_id']] = (row['start'], row['stop'])
        if groupclasses:
            data.append((row['start'], row['stop'],row['group_cls']))
			
        data.append((int(row['start']),int(row['stop']),t))
		
    if groups:
        for g in groupdata:
            data.append((int(groupdata[g][0]),int(groupdata[g][1]),g))

    			
    cats = {"music" : 0, "jingle": 1, "noise": 2 }
    specific_cats = {"speech M" : 3, "speech F": 4, "speech C": 5}

    if speakers or groups or groupclasses:

        if groups or groupclasses:
            cats.update(specific_cats)
	
        sids = [ d[2] for d in data ]
	
        specific_cats = {k: v+len(cats.keys()) for v, k in enumerate(list(set(sids)))}
	
        # remove possible duplicates
        for k in cats.keys():
            if k in specific_cats.keys(): del specific_cats[k]
			
	
    cats.update(specific_cats)
	
    # renumber
    cats = {k: v for v, k in enumerate(cats.keys())}

	
    colormapping = {}
	
    for k in cats.keys():
        colormapping[k] = "C"+str(cats[k])
	
    verts = []
    colors = []
    for d in data:
        v =  [(d[0], cats[d[2]]-.4),
              (d[0], cats[d[2]]+.4),
              (d[1], cats[d[2]]+.4),
              (d[1], cats[d[2]]-.4),
              (d[0], cats[d[2]]-.4)]
        verts.append(v)
        colors.append(colormapping[d[2]])

    bars = PolyCollection(verts, facecolors=colors)

    fig, ax = plt.subplots()
    ax.add_collection(bars)
    ax.autoscale()
	
    ax.set_yticks(list(range(len(cats))))
    ax.set_yticklabels(cats.keys())
	
    plt.savefig(fn)
	
if __name__ == "__main__":
    data = 'test'
    inafn = 'oe3wecker_20220804_result_ina.tsv'
    liumfn = 'oe3wecker_20220804_lium.out.seg'
    aaltofn = 'oe3wecker_20220804_aalto.out.seg'
	
    params = {}
    params['song_min_dur'] = 30
    params['grp_speaker_pause'] = 120
    params['grp_min_dur'] = 30
    
    ina_df = parse_ina(os.path.join(data,inafn))
	 
    lium_df = parse_lium(os.path.join(data,liumfn))
	 
    #aalto_df = parse_aalto(os.path.join(data,aaltofn))

	
    # news, weather, welcome
    #timerange = (0,400)
    # ad + news
    #timerange = (3420,4000)
	
    #timerange = (5000,5800)
    #timerange = (2300,2700)	
	
    #timerange = (0,2000)
    #timerange = (2000,4000)
    #timerange = (4000,6000)
    timerange = (6000,8000)
	
    #plot(lium_df,os.path.join(data,'plot_lium.png'),timerange)
	
    merged_df = merge_ina_lium(ina_df,lium_df)
    #merged2_df = merge_ina_lium(ina_df,aalto_df)
	
	
    merged_df = group_segments(merged_df,params)

    merged_df = classify_segments(merged_df,params)

    plot(merged_df,os.path.join(data,'plot_merged.png'),timerange)
    plot(merged_df,os.path.join(data,'plot_merged_speakers.png'),timerange,['speakers'])
   
    plot(merged_df,os.path.join(data,'plot_merged_groups.png'),timerange,['groups'])
  
    plot(merged_df,os.path.join(data,'plot_merged_group_cls.png'),timerange,['groupclasses'])
