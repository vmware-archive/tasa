# -*- coding: utf-8 -*-
'''
   Srivatsan Ramanujam <sramanujam@gopivotal.com>
   Wrapper for the Word-cloud generator.
'''

def parseFile(fname,filter_words):
    ''' Input file is of the form ||topic_num| num_words[optional] | word allocations || '''
    lines = open(fname).read().split('\n')
    lines = [l.replace('{','').replace('}','').replace('"','') for l in lines]
    lines = [l.split(';') for l in lines if l]
    
    #Remove filter words
    for l in range(len(lines)):
        word_list = lines[l][2].split(',')
        cleaned_words = [w for w in word_list if not filter_words.has_key(w.strip().lower())]
        lines[l][2] = cleaned_words
        	
    return lines

def filterTopOverlappingTokens(top_k,topic_words_list):
    '''
       Take the top-k words in each topic and remove all the words which occur in all the topics in any of  the top-10 positions
       These words are not representative of the topics, so we'll disregard them.
    '''
    from operator import itemgetter
    topk_dict = {}
    for item in topic_words_list:
        topic_num = item[0]
        word_allocs = item[2]
        for w in word_allocs:
            if(topk_dict.has_key(topic_num)):
                if(topk_dict[topic_num].has_key(w)):
                    topk_dict[topic_num][w]+=1
                else:
                    topk_dict[topic_num][w]=1
            else:
                topk_dict[topic_num] = {w:1}

    #Sort the dict to find top_k words under each topic.
    topk_list = []
    candidate_filter_tokens=[]
    for topic_num in topk_dict.keys():
        wlist = sorted([(key,val) for key,val in topk_dict[topic_num].items()],key=itemgetter(1),reverse=True)
        #Ensure there are atleast top_k tokens in the words for this topic
        top = top_k if(len(wlist)>= top_k) else len(wlist)
        candidate_filter_tokens.extend([(w,c) for w,c in wlist[:top]])
        topk_list.append([topic_num,wlist[:top]])

    candidate_filter_tokens = list(set(candidate_filter_tokens))

    #Now remove those tokens from the candidate list of tokens which occur in all topics
    remove_top_tokens={}
    for (tok,cnt) in candidate_filter_tokens:
        remove=True
        for wlist in topk_list:
            tok_lst = [w for w,c in wlist[1]]
            if tok not in tok_lst:
                remove=False
        if(remove):
            remove_top_tokens[tok]=1
    
    #Remove the overlapping tokens from topic_words_list
    for item in topic_words_list:
        for w in remove_top_tokens.keys():
            #Remove all occurrence of the top-k tokens
            item[2] = filter(lambda x: x!= w,item[2])
    return topic_words_list
    
