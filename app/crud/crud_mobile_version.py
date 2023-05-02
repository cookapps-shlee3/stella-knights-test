# -*- coding: utf-8 -*-
from platform import platform
from sqlalchemy.orm import Session
from app.db.models.mobile_version import MobileSpecVersion
from app.db.models.mobile_version import MobileLanguageVersion
from app.db.models.mobile_version import MobileVersion
from app.db.models.mobile_version import MobileSystemLanguageVersion
from app.db.models.mobile_version import MobileScenarioLanguageVersion
from app.db.models.mobile_version import MobileSpecDetailVersion





def get_app_spec_version_limit(db:Session, platform:str):
    return db.query(MobileSpecVersion).filter(MobileSpecVersion.platform == platform).first()


def get_app_lang_version_limit(db:Session, platform:str):
    return db.query(MobileLanguageVersion).filter(MobileLanguageVersion.platform == platform).first()

def get_app_system_lang_version_limit(db:Session, platform:str):
    return db.query(MobileSystemLanguageVersion).filter(MobileSystemLanguageVersion.platform == platform).first()

def get_app_scenario_lang_version_limit(db:Session, platform:str):
    return db.query(MobileScenarioLanguageVersion).filter(MobileScenarioLanguageVersion.platform == platform).first()


def check_version(db:Session, client_version:int):
    return db.query(MobileVersion).filter(MobileVersion.device == platform, MobileVersion.max_version >= client_version, MobileVersion.min_version <= client_version).first()


def get_version_info(db:Session, platform:str):
    return db.query(MobileVersion).filter(MobileVersion.device == platform).first()

def get_spec_detail_version_info(db:Session, platform:str):
    return db.query(MobileSpecDetailVersion).filter(MobileSpecDetailVersion.platform == platform).all()


