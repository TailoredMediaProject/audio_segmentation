#!/usr/bin/env python
# coding: utf-8

# In[3]:


from segwrapper import segwrapper


# In[7]:


media = '/inaSpeechSegmenter/media/11-00633_K01.mp3'


# In[8]:


segwrapper.ina_segmenter(media,'/results/ina.csv')


# In[9]:


get_ipython().system('/results/ina.csv')


# In[ ]:




