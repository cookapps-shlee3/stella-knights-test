# -*- coding: utf-8 -*-
import re
import json
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import Optional
from app.db.connection import get_db
from app.util.util import get


mmp_push_app_router = APIRouter()

column_array = [
    'app_name', 'app_token', 'user_id', 'is_organic', 'tracker', 'tracker_name', 'network_name',
    'campaign_id', 'campaign_name', 'adgroup_id', 'adgroup_name', 'creative_id', 'creative_name',
    'gps_adid', 'android_id', 'fire_adid', 'idfa', 'idfv', 'country', 'language', 'city',
    'cost_currency', 'postal_code', 'device_name', 'device_type', 'os_name', 'store', 'platform', 'api_level',
    'sdk_version', 'os_version', 'timezone', 'ip_address', 'is_reattributed', 'created_at', 'click_time', 'installed_at',
    'first_tracker', 'first_tracker_name', 'last_tracker', 'last_tracker_name', 'click_referer', 'referrer'
];


column_array_event = [
    'app_name', 'app_token', 'user_id', 'is_organic', 'tracker', 'tracker_name', 'network_name',
    'campaign_id', 'campaign_name', 'adgroup_id', 'adgroup_name', 'creative_id', 'creative_name',
    'gps_adid', 'android_id', 'fire_adid', 'idfa', 'idfv', 'country', 'language', 'city',
    'cost_currency', 'postal_code', 'device_name', 'device_type', 'os_name', 'store', 'platform', 'api_level',
    'sdk_version', 'os_version', 'timezone', 'ip_address', 'is_reattributed', 'created_at', 'click_time', 'installed_at',
    'first_tracker', 'first_tracker_name', 'last_tracker', 'last_tracker_name', 'click_referer', 'referrer', 'event_name'
];


@mmp_push_app_router.get("/mmp-push")
async def set_adjust_push_get(req:Request, db:Session = Depends(get_db)):
    network_name = str(req.query_params.get('network_name', default=''))
    campaign_name = str(req.query_params.get('campaign_name', default=''))
    adgroup_name = str(req.query_params.get('adgroup_name', default=''))
    creative_name = str(req.query_params.get('creative_name', default=''))
    
    queryParams = {}
        
    if network_name.lower() != 'organic':
        if network_name() == 'cookapps':
            ## 쿡앱스 크로스 프로모션, campaign_id, adgroup_id, creative_id 처리
            queryParams['campaign_id'] = campaign_name;
            queryParams['adgroup_id'] = adgroup_name;
            queryParams['creative_id'] = creative_name;
        elif network_name.find('Untrusted Devices') >= 0:
            queryParams['first_tracker_name'] = 'Organic';
            queryParams['network_name'] = 'Organic';
            queryParams['campaign_name'] = 'Untrusted Devices';
            queryParams['campaign_id'] = 'Untrusted Devices';
    else:
        ## FB 먼저 체크
        if req.query_params.get('fb_install_referrer'):
            queryParams['tracker_name'] = 'Facebook Ads';
            queryParams['network_name'] = 'Facebook Ads';

            fb_install_referrer = json.loads(req.query_params.get('fb_install_referrer'))

            queryParams['campaign_name'] = get(fb_install_referrer, 'campaign_group_name', default='')
            queryParams['campaign_id'] = get(fb_install_referrer, 'campaign_group_id', default='')
            queryParams['adgroup_name'] = get(fb_install_referrer, 'campaign_name', default='')
            queryParams['adgroup_id'] = get(fb_install_referrer, 'campaign_id', default='')
            queryParams['creative_name'] = get(fb_install_referrer, 'adgroup_name', default='')
            queryParams['creative_id'] = get(fb_install_referrer, 'adgroup_id', default='')
        else:
            
            if req.query_params.get('campaign_id', default=''):
                matches = re.findall('/\(.*?\)/', req.query_params.get('campaign_id'))
                
                if len(matches) == 0:
                    queryParams['campaign_id'] = campaign_name
                else:
                    queryParams['campaign_id'] = re.sub('preg_replace', '', matches[0])

            if adgroup_name != '':
                matches = re.findall('/\(.*?\)/', adgroup_name)
                
                if len(matches) == 0:
                    queryParams['adgroup_id'] = adgroup_name
                else:
                    queryParams['adgroup_id'] = re.sub('preg_replace', '', matches[0])
                
            if creative_name != '':
                matches = re.findall('/\(.*?\)/', creative_name)
                
                if len(matches) == 0:
                    queryParams['creative_id'] = creative_name
                else:
                    queryParams['creative_id'] = re.sub('preg_replace', '', matches[0])
    
    idx = 0
    keys = ''
    values = ''
    
    for column in column_array:
        if column not in queryParams:
            queryParams[column] = str(req.query_params.get(column, default='')).replace("'", "\\'")
    
    placeholders = ', '.join(['%s'] * len(queryParams))
    columns = ', '.join(queryParams.keys())

    
    sql = "INSERT INTO %s ( %s ) VALUES %s" % ('mmp_push_app_install', columns, tuple(queryParams.values()))
    db.execute(sql)
    db.commit()

    return 


@mmp_push_app_router.post("/mmp-push")
async def set_adjust_push_post(req:Request, db:Session = Depends(get_db)):
    
    return 




@mmp_push_app_router.get("/mmp-push-event")
async def set_adjust_push_event_get(req:Request, db:Session = Depends(get_db)):
    network_name = str(req.query_params.get('network_name', default=''))
    campaign_name = str(req.query_params.get('campaign_name', default=''))
    adgroup_name = str(req.query_params.get('adgroup_name', default=''))
    creative_name = str(req.query_params.get('creative_name', default=''))
    
    queryParams = {}
        
    if network_name.lower() != 'organic':
        if network_name() == 'cookapps':
            ## 쿡앱스 크로스 프로모션, campaign_id, adgroup_id, creative_id 처리
            queryParams['campaign_id'] = campaign_name;
            queryParams['adgroup_id'] = adgroup_name;
            queryParams['creative_id'] = creative_name;
        elif network_name.find('Untrusted Devices') >= 0:
            queryParams['first_tracker_name'] = 'Organic';
            queryParams['network_name'] = 'Organic';
            queryParams['campaign_name'] = 'Untrusted Devices';
            queryParams['campaign_id'] = 'Untrusted Devices';
    else:
        ## FB 먼저 체크
        if req.query_params.get('fb_install_referrer'):
            queryParams['tracker_name'] = 'Facebook Ads';
            queryParams['network_name'] = 'Facebook Ads';

            fb_install_referrer = json.loads(req.query_params.get('fb_install_referrer'))

            queryParams['campaign_name'] = get(fb_install_referrer, 'campaign_group_name', default='')
            queryParams['campaign_id'] = get(fb_install_referrer, 'campaign_group_id', default='')
            queryParams['adgroup_name'] = get(fb_install_referrer, 'campaign_name', default='')
            queryParams['adgroup_id'] = get(fb_install_referrer, 'campaign_id', default='')
            queryParams['creative_name'] = get(fb_install_referrer, 'adgroup_name', default='')
            queryParams['creative_id'] = get(fb_install_referrer, 'adgroup_id', default='')
        else:
            
            if req.query_params.get('campaign_id', default=''):
                matches = re.findall('/\(.*?\)/', req.query_params.get('campaign_id'))
                
                if len(matches) == 0:
                    queryParams['campaign_id'] = campaign_name
                else:
                    queryParams['campaign_id'] = re.sub('preg_replace', '', matches[0])

            if adgroup_name != '':
                matches = re.findall('/\(.*?\)/', adgroup_name)
                
                if len(matches) == 0:
                    queryParams['adgroup_id'] = adgroup_name
                else:
                    queryParams['adgroup_id'] = re.sub('preg_replace', '', matches[0])
                
            if creative_name != '':
                matches = re.findall('/\(.*?\)/', creative_name)
                
                if len(matches) == 0:
                    queryParams['creative_id'] = creative_name
                else:
                    queryParams['creative_id'] = re.sub('preg_replace', '', matches[0])
    
    idx = 0
    keys = ''
    values = ''
    
    for column in column_array_event:
        if column not in queryParams:
            queryParams[column] = str(req.query_params.get(column, default='')).replace("'", "\\'")
    
    placeholders = ', '.join(['%s'] * len(queryParams))
    columns = ', '.join(queryParams.keys())

    
    sql = "INSERT INTO %s ( %s ) VALUES %s" % ('mmp_push_app_install', columns, tuple(queryParams.values()))
    db.execute(sql)
    db.commit()
    
    return 

   

@mmp_push_app_router.post("/mmp-push-event")
async def set_adjust_push_event_post(req:Request, db:Session = Depends(get_db)):
    return 



