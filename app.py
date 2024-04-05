import codecs
import datetime
import json
import os
import ast
import io
import zipfile
from flask_sqlalchemy import SQLAlchemy  # Create DB with Flask
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, send_file, session, Response  # Package for Routing
from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, DateTime, inspect, Float, func, or_, \
    BigInteger  # DB Column Datatype
from sqlalchemy.orm import relationship, backref  # Create DB Relationship
from sqlalchemy.orm.exc import DetachedInstanceError  # DB Session lock error
import math
import csv
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user  # Login Module
from functools import wraps
from flask import abort
from werkzeug.security import generate_password_hash, check_password_hash
from forms import *
import random
from functions import FR, N1, N2, N4, N5_in, N6_lbhr_psi_lbft3, N7_60_scfh_psi_F, N8_kghr_bar_K, N9_O_m3hr_kPa_C, REv, conver_FR_noise, convert_T_SI, full_format, getBooleanFromString, getFlowCharacter, getValveType, meta_convert_P_T_FR_L, project_status_list, notes_dict_reorder, purpose_list, units_dict, actuator_data_dict, valve_force_dict,meta_convert_g_to_a,meta_convert_a_to_g
from gas_noise_formulae import getPowerLevelGas, lpae_1m
from gas_velocity_iec import getGasVelocities
from liquid_noise_formulae import Lpe1m, mechanicalPower
from sqlalchemy.sql.sqltypes import String, VARCHAR, FLOAT, INTEGER
from jinja2 import Environment, FileSystemLoader
import smtplib
from specsheet import createSpecSheet,createcvOpening_gas,createActSpecSheet
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dateutil.parser import parse
from models import *
from flask_migrate import Migrate
from dbsetup import db
from fractions import Fraction
from decimal import Decimal

# -----------^^^^^^^^^^^^^^----------------- IMPORT STATEMENTS -----------------^^^^^^^^^^^^^------------ #

# env = Environment(loader=FileSystemLoader('templates\\render_data.html'))
# env.globals['getattr'] = getattr

def getRowsFromCsvFile(file_path):
    filename = file_path
    fields_afr = []
    rows_afr = []

    # reading csv file
    with open(filename, 'r', encoding='utf-8-sig') as csvfile:
        # creating a csv reader object
        csvreader = csv.reader(csvfile)

        # extracting field names through first row
        fields_afr = next(csvreader)

        # extracting each data row one by one
        for row in csvreader:
            dict_add = {}
            for i in range(len(fields_afr)):
                dict_add[fields_afr[i]] = row[i]
            rows_afr.append(dict_add)

    return rows_afr


### --------------------------------- APP CONFIGURATION -----------------------------------------------------###

# app configuration
app = Flask(__name__)

app.config['SECRET_KEY'] = "kkkkk"
Bootstrap(app)

# # CONNECT TO DB
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///fcc-db-v6-0.db"

# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL1", "sqlite:///fcc-db-v10-0.db")
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Qwer1234@localhost/ValveSizingFCC'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)


# creating login manager
login_manager = LoginManager()
login_manager.init_app(app)


# Create admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        admin = userMaster.query.all()
        admin_id = []
        for i in admin:
            id_ = i.id
            admin_id.append(id_)

        if current_user.id not in admin_id:
            return abort(403)
        # Otherwise, continue with the route function
        return f(*args, **kwargs)

    return decorated_function


@login_manager.user_loader
def load_user(user_id):
    return userMaster.query.get(int(user_id))






# TODO Other DAta
table_data_render = [
    {'name': 'Project Data', 'db': projectMaster, 'id': 1},
    {'name': 'Industry Data', 'db': industryMaster, 'id': 2},
    {'name': 'Region Data', 'db': regionMaster, 'id': 3},
    {'name': 'Engineer', 'db': engineerMaster, 'id': 4},
    {'name': 'Item', 'db': itemMaster, 'id': 5},
    {'name': 'Valve Style', 'db': valveStyle, 'id': 6},
    {'name': 'Rating', 'db': ratingMaster, 'id': 7},
    {'name': 'Material', 'db': materialMaster, 'id': 8},
    {'name': 'Standard Master', 'db': designStandard, 'id': 9},
    {'name': 'Fluid Type', 'db': fluidState, 'id': 10},
    {'name': 'Application', 'db': applicationMaster, 'id': 11},
    {'name': 'End Connection', 'db': endConnection, 'id': 12},
    {'name': 'End Finish', 'db': endFinish, 'id': 13},
    {'name': 'Bonnet Type', 'db': bonnetType, 'id': 14},
    {'name': 'PackingT ype', 'db': packingType, 'id': 15},
    {'name': 'Trim Type', 'db': trimType, 'id': 16},
    {'name': 'Flow Direction', 'db': flowDirection, 'id': 17},
    {'name': 'Leakage Class', 'db': seatLeakageClass, 'id': 18},
    {'name': 'Cleaning', 'db': cleaning, 'id': 19},
    {'name': 'Certification', 'db': certification, 'id': 20},
    {'name': 'Paint Finish', 'db': paintFinish, 'id': 21},
    {'name': 'Paint Certs', 'db': paintCerts, 'id': 22},
    {'name': 'Pipe Area', 'db': pipeArea, 'id': 23},
    {'name': 'Valve Area', 'db': valveArea, 'id': 24},
    {'name': 'Pressure Temperature', 'db': pressureTempRating, 'id': 25},
    {'name': 'Design Standard', 'db': designStandard, 'id': 26},
    {'name': 'Balance Seal', 'db': balanceSeal, 'id': 27},
    {'name': 'Balancing', 'db': balancing, 'id': 28},
    {'name': 'Bonnet', 'db': bonnet, 'id': 29},
    {'name': 'End Connection', 'db': endConnection, 'id': 30},
    {'name': 'End Finish', 'db': endFinish, 'id': 31},
    {'name': 'Flow Character', 'db': flowCharacter, 'id': 32},
    {'name': 'Fluid State', 'db': fluidState, 'id': 33},
    {'name': 'Gasket', 'db': gasket, 'id': 34},
    {'name': 'Packing Type', 'db': packingType, 'id': 35},
    {'name': 'Paint Certificates', 'db': paintCerts, 'id': 36},
    {'name': 'Paint Finish', 'db': paintFinish, 'id': 37},
    {'name': 'Limit Switch', 'db': limitSwitch, 'id': 38},
    {'name': 'AFR', 'db': afr, 'id': 39},
    {'name': 'Engineer Master', 'db': engineerMaster, 'id': 40},
    {'name': 'Fluid Properties', 'db': fluidProperties, 'id': 41},
    {'name': 'Positioner', 'db': positioner, 'id': 42},
    {'name': 'Positioner Signal', 'db': positionerSignal, 'id': 43},
    {'name': 'Packing Friction', 'db': packingFriction, 'id': 44},
    {'name': 'Packing Torque', 'db': packingTorque, 'id': 45},
    {'name': 'Port Area', 'db': portArea, 'id': 46},
    {'name': 'Seat', 'db': seat, 'id': 47},
    {'name': 'Seat Load Force', 'db': seatLoadForce, 'id': 48},
    {'name': 'Seating Torque', 'db': seatingTorque, 'id': 49},
    {'name': 'Shaft', 'db': shaft, 'id': 50},
    {'name': 'Packing', 'db': packing, 'id': 51},
    {'name': 'Kn Values', 'db': knValue, 'id': 52},
    {'name': 'HW Thrust', 'db': hwThrust, 'id': 53},
    {'name': 'Solenoid', 'db': solenoid, 'id': 54},
]


### ----------------------------------------- Actuator Functions --------------------------------#
def valveForces(p1_, p2_, d1, d2, d3, ua, rating, material, leakageClass, trimtype, balance, flow,
                case, shutoffDelP,packingF,seatF):
    print('Valve forces inputs:')
    print(p1_, p2_, d1, d2, d3, ua, rating, material, leakageClass, trimtype, balance, flow,
          case, shutoffDelP,packingF,seatF)
    num = 0

    # if trimtype.name == 'Contour':
    #     flow = 'under'
    #     balance = 'unbalanced'
    # if balance == 'Unbalanced' or balance == 'unbalanced':
    #     balance_in = 'unbalanced'
    # elif balance == 'Balanced' or balance == 'balanced':
    #     balance_in = 'balanced'
    # print(f'balance_in {trimtype.name},{balance_in}')
    if d1 in [1, 3, 8, 11, 4]:
        d1 = round(d1)
    p1 = p1_
    p2 = p2_
    a1 = 0.785 * d1 * d1  # seat bore - seat dia
    a2 = 0.785 * d2 * d2  # plug dia
    a3 = 0.785 * d3 * d3  # stem dia
    shutoffDelP = shutoffDelP 

    with app.app_context():
        friction_element = db.session.query(packingFriction).filter_by(rating=rating, packing_=material).order_by(func.abs(packingFriction.stemDia - d3)).first()
        # print(float(friction_element.value))
        sf_element = db.session.query(seatLoadForce).filter_by(trimType_=trimtype, leakage=leakageClass).order_by(func.abs(seatLoadForce.seatBore - d1)).first()
        # print(trimtype, d1)
        try:
            B = float(packingF)
            C = math.pi * d1 * float(seatF)
        except AttributeError:
            B = 0
            C = 0
        print(f"Packing friction: {B}, Seat Load Force: {C}")
    print((trimtype, balance, flow, case))
    # Trimtype, balance, flow logic
    if trimtype.name in ['Contour', 'Microspline']:
        trimtype_in = "contour"
    else:
        trimtype_in = "cage"
    
    if balance.name == 'Balanced':
        balance_in = 'balanced' 
    else:
        balance_in = 'unbalanced'
    print(f'jsjsshHhshhshshs {balance}')


    print(f'balance {(trimtype_in, balance_in, flow.name.lower(), case)}')
    for i in valve_force_dict:
        if i['key'] == (trimtype_in, balance_in, flow.name.lower(), case):
            num = int(i['formula'])
    print(f'num: {num}')
    if num == 1:
        a_ = shutoffDelP * a1 # Shutoff
        UA = a1
    elif num == 2:
        a_ = shutoffDelP * a1
        UA = a1
    elif num == 3:
        a_ = shutoffDelP * (a3 - a1)
        UA = a3 - a1
    elif num == 4:
        a_ = shutoffDelP * (a3 - ua)
        UA = ua
    elif num == 5:
        a_ = shutoffDelP * ua
        UA = ua
    elif num in [6,7]:
        a_ = (shutoffDelP * a1) + B + C # Shutoff+
        UA = a1
        print(f'KSKKSKSKSKYYYYYYYYY {(shutoffDelP * a1)}, {a_}, {p1}, {a1}')

    elif num == 8:
        a_ = (shutoffDelP * (a3 - a1)) + B + C
        UA = a3 - a1
    elif num == 9:
        a_ = shutoffDelP * (a3 - ua) + B + C
        UA = ua
        print(f"inputs for equation 9: {a3, ua, shutoffDelP, B, C}")
    elif num == 10:
        a_ = (shutoffDelP * ua) + B + C
        UA = ua
    elif num in [11, 12]:
        a_ = (p1 * a1) + (p2 * (a2 - a1)) - (p2 * (a2 - a3)) # Close
        print(f"eq 11 or 12 inputs: {p1}, {p2}, {a1}, {a2}, {a3}")
        UA = a2 - a1
    elif num == 13:
        a_ = p1 * (a2 - a1) + p2 * a1 - p1 * (a2 - a3)
        UA = a2 - a1
    elif num == 14:
        a_ = p1 * a1 + p2 * (a2 - a1) - p1 * (a2 - a3)
        UA = a2 - a1
    elif num == 15:
        a_ = p1 * (a2 - a1) + p2 * a1 - p2 * (a2 - a3)
        UA = a2 - a1
    elif num in [16, 17, 19]:
        a_ = ((p1 * a2) - (p2 * (a2 - a3)) ) + B # Open
        print(f"eq 16 inputs: {p1}, {p2}, {a2}, {a3}")
        UA = a2 - a1
    elif num in [18, 20]:
        print(f'VOPEN___b4 {p2},{a2},{p1},{a2},{a3},{B}')
        a_ = ((p2 * a2) - (p1 * (a2 - a3)) ) + B
        if a_ < 0:
            a_ = B
        print(f'VOPEN____ {a_}')
        UA = a2 - a1
    else:
        a_ = 1
        UA = a2 - a1

    return_list = [round(a_, 3), UA, B, sf_element.value, friction_element, sf_element, C]

    return return_list




### --------------------------------- Major Functions -----------------------------------------------------###

def getModelValve(series, rating, trim_type, temperature, seal, balance, temp_unit):
    with app.app_context():
    # Rating factor
        all_ratings = ratingMaster.query.all()
        all_ratings_name = [ratings.name for ratings in all_ratings]
        print(all_ratings_name)
        rating_index = all_ratings_name.index(rating) + 1
        if rating_index <= 6:
            rating_factor = str(rating_index)
        else:
            rating_factor = 'X'
        
        # Trim Factor
        if trim_type == 'Triple Offset':
            trim_factor = '30'
        elif trim_type == 'Double Offset':
            if seal == 'soft':
                trim_factor = '10'
            else:
                trim_factor = '20'
        elif trim_type == 'Contour':
            trim_factor = '10'
        elif trim_type == 'Microspline':
            trim_factor = '20'
        elif trim_type == 'Ported':
            if balance == 'Unbalanced':
                trim_factor = '30'
            else:
                trim_factor = '40'
        else:
            trim_factor = 'X1'

        # Temp factor
        temp_c = convert_T_SI(temperature, temp_unit, 'C', 1000)
        if -29 <= temp_c < 232:
            temp_factor = '1'
        elif 232 <= temp_c < 427:
            temp_factor = '4'
        elif temp_c >= 427:
            temp_factor = '3'
        else:
            temp_factor = '2'
        

        model_no = str(series) + rating_factor + trim_factor + temp_factor
        return model_no




valve_table_dict_two = {'ratingId': ratingMaster, 'materialId': materialMaster, 'designStandardId': designStandard, 'valveStyleId': valveStyle, 'fluidStateId': fluidState, 'endConnectionId': endConnection, 'endFinishId': endFinish, 'bonnetTypeId': bonnetType, 'packingTypeId': packingType, 'trimTypeId': trimType, 'flowCharacterId': flowCharacter, 'flowDirectionId': flowDirection, 'seatLeakageClassId': seatLeakageClass, 'bonnetId': bonnet, 'nde1Id': '', 'nde2Id': '', 'shaftId': shaft, 'discId': disc, 'seatId': seat, 'packingId': packing, 'balanceSealId': balanceSeal, 'studNutId': studNut, 'gasketId': gasket, 'cageId': cageClamp}



# Delete completed data in db table
def data_delete(table_name):
    # with app.app_context():
    data_list = table_name.query.all()
    print(f'len of all elements: {len(data_list)}')
    # db.session.commit()
    # if len(data_list) > 0:
    for data_ in data_list:
        data_element = db.session.query(table_name).filter_by(id=data_.id).first()
        # db.session.commit()
        db.session.delete(data_element)
        db.session.commit()


def next_alpha(s):
    return chr((ord(s.upper()) + 1 - 65) % 26 + 65)


# Data upload function   lllll
def data_upload(data_list, table_name):
    # with app.app_context():
    print(f"data delete starts: {table_name.__tablename__}")
    data_delete(table_name)
    print("data delete ends")
    print('dataupload starts')
    all_data = table_name.query.all()
            
    new_count = 0
    for data_ in data_list:
        data_element = db.session.query(table_name).filter_by(name=data_).all()
        if len(data_element) == 0:
            # print(data_)
            new_data = table_name(name=data_)
            db.session.add(new_data)
            db.session.commit()
            new_count += 1
        elif len(data_element) > 1:
            for data__ in data_element[1:]:
                data_element = db.session.query(table_name).filter_by(id=data__.id).first()
                db.session.delete(data_element)
                db.session.commit()
                # print(f"Deleted: {data__}, {data_element.index(data__)}")
    
    print(new_count)
    print('data upload ends')


def pressure_temp_upload(data_set):
    # with app.app_context():
    # data_d_list = pressureTempRating.query.all()
    data_delete(pressureTempRating)
    for data_ in data_set:
        material_element = db.session.query(materialMaster).filter_by(name=data_['material']).first()
        rating_element = db.session.query(ratingMaster).filter_by(name=data_['rating']).first()
        new_data = pressureTempRating(maxTemp=float(data_['maxTemp']), minTemp=float(data_['minTemp']),
                                        pressure=float(data_['pressure']), material=material_element, rating=rating_element)
        db.session.add(new_data)
        db.session.commit()



def getList(dict_):
    list = []
    for key in dict_.keys():
        list.append(key)
         
    return list

def packing_friction_upload(data_set):
    data_delete(packingFriction)
    key_list = getList(data_set[0])
    for data_ in data_set:
        stem_dia = float(data_['stemDia'])
        rating_element = db.session.query(ratingMaster).filter_by(name=data_['rating']).first()
        for key_ in key_list[2:]:
            packing_element = db.session.query(packing).filter_by(name=key_).first()
            new_packing_friction = packingFriction(stemDia=stem_dia, rating=rating_element, packing_=packing_element, value=data_[key_])
            db.session.add(new_packing_friction)
            db.session.commit()

def seat_load_force_upload(data_set):
    data_delete(seatLoadForce)
    key_list = getList(data_set[0])
    print(key_list)
    for data_ in data_set:
        stem_dia = float(data_['stemDia'])
        trimType_element = db.session.query(trimType).filter_by(name=data_['trimType_']).first()
        for key_ in key_list[2:]:
            leakage_element = db.session.query(seatLeakageClass).filter_by(name=key_).first()
            new_seat_load = seatLoadForce(seatBore=stem_dia, trimType_=trimType_element, leakage=leakage_element, value=data_[key_])
            db.session.add(new_seat_load)
            db.session.commit()

def add_many(list_many, table_name):
    print(f'LLLLLLLLL {list_many},{table_name}')

    data_delete(table_name)
    for i in list_many:
        new_object = table_name()
        db.session.add(new_object)
        db.session.commit()
        # print(i)
        keys = i.keys()
        last_object = table_name.query.all()
        for key in keys:
            key_type = table_name.__table__.columns[key].type
            if key_type == String or VARCHAR:
                exec("last_object[-1].{0} = i['{0}']".format(key))
            elif key_type == FLOAT:
                exec("last_object[-1].{0} = float(i['{0}'])".format(key))
            elif key_type == INTEGER:
                exec("last_object[-1].{0} = int(i['{0}'])".format(key))
        db.session.commit()
    # db.session.add_all(list_many)
    # db.session.commit()
def knValue_upload(data_list):
    print("delete begin: UA")
    data_delete(knValue)
    print("delete done: UA")
    print("Data Upload UA Start")
    print(data_list)
    cnt = 0
    for i in range(len(data_list)):

        flowdir_ = db.session.query(flowDirection).filter_by(name=data_list[i]['flowDirection']).first()
        flowchar_ = db.session.query(flowCharacter).filter_by(name=data_list[i]['flowCharac']).first()
        if(data_list[i]['trimType'] == 'except noise and cavity'):
            trim_elements = db.session.query(trimType)\
                .filter_by(valveStyleId=1)\
                .filter(~trimType.name.like('Low%') & ~trimType.name.like('Anti%'))\
                .all()
            print(f'trim {trim_elements}')

        elif (data_list[i]['trimType'] == 'Low Noise Trim'):
            trim_elements = db.session.query(trimType)\
                .filter_by(valveStyleId=1)\
                .filter(trimType.name.like('Low%'))\
                .all()
        else:
            trim_elements = db.session.query(trimType)\
                .filter_by(valveStyleId=1)\
                .filter_by(name = data_list[i]['trimType'])\
                .all() 
        for trim_ in trim_elements:
            cnt += 1
            knvalue_ = knValue(
                portDia = data_list[i]['portDia'],
                series = data_list[i]['series'],
                trimType_ = trim_,
                flowCharacter_ = flowchar_,
                flowDirection_ = flowdir_,
                value = data_list[i]['Kn']

            )
            print(f' totalkn {cnt}')
            db.session.add(knvalue_)
            db.session.commit()

def unbalanceArea_upload(data_list):
    print("delete begin: UA")
    data_delete(unbalanceAreaTb)
    print("delete done: UA")
    print("Data Upload UA Start")
    # print(data_list)
    cnt=0
    for i in range(len(data_list)):
        trim_type_element = db.session.query(trimType).filter_by(name=data_list[i]['trimType']).first()
        # print(f'TRIMTYPE {trim_type_element} , {data_list[i]['trimType']}')
        if data_list[i]['trimType'] == 'Low Noise Trim A1':
            low_trim_elements = db.session.query(trimType)\
                .filter_by(valveStyleId = 1)\
                .filter(trimType.name.like('Low%'))\
                .all()
            print(f'TRIMTYPE {trim_type_element} , {low_trim_elements}')
        else:
            print(f'TRIMTYPE {trim_type_element} , {data_list[i]['trimType']}')



        leakageClass = db.session.query(seatLeakageClass).all()
        if data_list[i]['leakageClass'] == 'All':
            for leakage_ in leakageClass:
                if data_list[i]['trimType'] == 'Low Noise Trim A1':
                    for trim_ in low_trim_elements:
                        ua_datas = unbalanceAreaTb(
                            seatDia=data_list[i]['seatDia'],
                            plugDia=data_list[i]['plugDia'],
                            Ua=data_list[i]['Ua '],
                            trimType_=trim_,
                            seatLeakageClass__=leakage_,
                        )
                        cnt+=1
                        db.session.add(ua_datas)
                        db.session.commit()
                else:
                    ua_datas = unbalanceAreaTb(
                            seatDia=data_list[i]['seatDia'],
                            plugDia=data_list[i]['plugDia'],
                            Ua=data_list[i]['Ua '],
                            trimType_=trim_type_element,
                            seatLeakageClass__=leakage_,
                        )
                    cnt+=1
                    db.session.add(ua_datas)
                    db.session.commit()
        elif data_list[i]['leakageClass'] == 'Except Class V':
            for leakage_ in leakageClass:
                if leakage_.name != 'ANSI Class V':
                        if data_list[i]['trimType'] == 'Low Noise Trim A1':
                            for trim_ in low_trim_elements:
                                ua_datas = unbalanceAreaTb(
                                    seatDia=data_list[i]['seatDia'],
                                    plugDia=data_list[i]['plugDia'],
                                    Ua=data_list[i]['Ua '],
                                    trimType_=trim_,
                                    seatLeakageClass__=leakage_,
                                )
                                cnt+=1
                                db.session.add(ua_datas)
                                db.session.commit()
                        else:
                            ua_datas = unbalanceAreaTb(
                                    seatDia=data_list[i]['seatDia'],
                                    plugDia=data_list[i]['plugDia'],
                                    Ua=data_list[i]['Ua '],
                                    trimType_=trim_type_element,
                                    seatLeakageClass__=leakage_,
                                )
                            cnt+=1
                            db.session.add(ua_datas)
                            db.session.commit()
                            

        elif data_list[i]['leakageClass'] == 'Class V':
            for leakage_ in leakageClass:
                if leakage_.name == 'ANSI Class V':
                        if data_list[i]['trimType'] == 'Low Noise Trim A1':
                            for trim_ in low_trim_elements:
                                ua_datas = unbalanceAreaTb(
                                    seatDia=data_list[i]['seatDia'],
                                    plugDia=data_list[i]['plugDia'],
                                    Ua=data_list[i]['Ua '],
                                    trimType_=trim_,
                                    seatLeakageClass__=leakage_,
                                )
                                cnt+=1
                                db.session.add(ua_datas)
                                db.session.commit()
                        else:
                            ua_datas = unbalanceAreaTb(
                                    seatDia=data_list[i]['seatDia'],
                                    plugDia=data_list[i]['plugDia'],
                                    Ua=data_list[i]['Ua '],
                                    trimType_=trim_type_element,
                                    seatLeakageClass__=leakage_,
                                )
                            cnt+=1
                            db.session.add(ua_datas)
                            db.session.commit()
                            



    print(f"Data Upload UA End {cnt}")


def hwThrust_upload(data_list):
    print("delete begin: HW")
    # # data_delete(cvValues)
    data_delete(hwThrust)
    print("delete done: HW")
    print(f"Data Upload HW Start {len(data_list)}")
    print(data_list)
    for data in data_list:
        hwThrust_ = hwThrust(
            failAction = data['failAction'],
            mount = data['handwheel'],
            ac_size = data['actuatorSize'],
            max_thrust = data['maxHWThrust'],
            dia = data['handwheelDia']
        )

        db.session.add(hwThrust_)
        db.session.commit()

def shaft_rotary_upload(data_list):
    print("delete begin: SR")
    # # data_delete(cvValues)
    data_delete(shaftRotary)
    print("delete done: SR")
    print(f"Data Upload SR Start {data_list}")
    
    for data in data_list:
        print(f'ratingPRESSURE {data['ratingPressure']}')
        rating_element = db.session.query(ratingMaster).filter_by(
        name=data['ratingPressure']).first()
        print(f'rating_element {rating_element}')
        shaftRotary_ = shaftRotary(
            rating = rating_element,
            valveSize = data['valveSize'],
            stemDia = data['shaftDia'],
            valveInterface = data['valveInterface'] 
        )

        db.session.add(shaftRotary_)
        db.session.commit()
        print('END')



def rotary_upload(data_list):
    print("delete begin: AD")
    # # data_delete(cvValues)
    data_delete(rotaryActuatorData)
    print("delete done: AD")
    print(f"Data Upload AD Start {len(data_list)}")
    
    for data in data_list:
        rotaryActuator_ = rotaryActuatorData(
            actType = data['actType'],
            failAction = data['failAction'],
            valveInterface = data['valveInterface'],
            actSize_ = data['actSize_'],
            springSet = data['springSet'],
            torqueType = data['torqueType'],
            setPressure = data['setPressure'],
            start = float(data['start']),
            mid = float(data['mid']),
            end = float(data['end']),
            actSize = float(data['actSize']),
        
        )

        db.session.add(rotaryActuator_)
        db.session.commit()
        print('END')

def seating_torque_upload(data_list):
    print("delete begin: ST")

    data_delete(seatingTorque)
    print("delete done: ST")
    print(f"Data Upload ST Start {len(data_list)}")
    print(data_list)
    for data in data_list:
        seatingTorque_ = seatingTorque(
            valveSize = float(data['valveSize']),
            discDia = float(data['discDia']),
            discDia2 = float(data['discDia2']),
            cusc = float(data['cUsc']),
            cusp = float(data['cUsp']),
            softSeatA = float(data['softSeatA']),
            softSeatB = float(data['softSeatB']),
            metalSeatA = float(data['metalSeatA']),
            metalSeatB = float(data['metalSeatB'])
        
        )

        db.session.add(seatingTorque_)
        db.session.commit()







def yieldStrength_upload(data_list):
    print("delete begin: YD")
    # # data_delete(cvValues)
    data_delete(yieldStrength)
    print("delete done: HW")
    print(f"Data Upload HW Start {len(data_list)}")
    print(data_list)
    for data in data_list:
        yieldStrength_ = yieldStrength(
            shaft_material = data['shaftMaterial'],
            yield_strength = data['yieldStrength'],
        
        )

        db.session.add(yieldStrength_)
        db.session.commit()









def cv_upload(data_list):
    # with app.app_context():
    print("delete begin: CV")
    # # data_delete(cvValues)
    data_delete(cvTable)
    print("delete done: CV")
    print("Data Upload CV Start")
    new_data_list = data_list[::4]  # Get every fourth element from the list
    len_data = len(new_data_list)
    new_count = 0
    for data_index in range(len_data):
        # Get DB Element
        trim_type_element = db.session.query(trimType).filter_by(
            name=new_data_list[data_index]['trimType_']).first()
        flow_charac_element = db.session.query(flowCharacter).filter_by(
            name=new_data_list[data_index]['flowCharacter_']).first()
        flow_direction_element = db.session.query(flowDirection).filter_by(
            name=new_data_list[data_index]['flowDirection_']).first()
        balancing_element = db.session.query(balancing).filter_by(
            name=new_data_list[data_index]['balancing_']).first()
        rating_element = db.session.query(ratingMaster).filter_by(
            name=new_data_list[data_index]['rating_c']).first()
        v_style_element = db.session.query(valveStyle).filter_by(name=new_data_list[data_index]['style']).first()
        valve_size = float(new_data_list[data_index]['valveSize'])
        series = new_data_list[data_index]['series']
        
        # cv__lists = db.session.query(cvTable).filter_by(trimType_=trim_type_element, flowCharacter_=flow_charac_element, flowDirection_=flow_direction_element, rating_c=rating_element, style=v_style_element, balancing_=balancing_element, valveSize=valve_size).all()

        
        # if len(cv__lists) == 0:
            # print(data_)
        new_cv_table_entry = cvTable(
            valveSize=valve_size,
            series=series,
            trimType_=trim_type_element,
            flowCharacter_=flow_charac_element,
            flowDirection_=flow_direction_element,
            balancing_=balancing_element,
            rating_c=rating_element,
            style=v_style_element
        )
        db.session.add(new_cv_table_entry)
        db.session.commit()
        new_count += 1
        # elif len(cv__lists) > 1:
        #     for data__ in cv__lists[1:]:
        #         data_element = db.session.query(cvTable).filter_by(id=data__.id).first()
        #         db.session.delete(data_element)
        #         db.session.commit()
    
        # Add CV Table Data
        # print(new_data_list[data_index]['no'], trim_type_element.name, flow_charac_element.name, flow_direction_element.name, balancing_element.name, rating_element.name, v_style_element.name)
        # if len(cv__lists) == 0:
        #     new_cv_table_entry = cvTable(
        #         valveSize=valve_size,
        #         series=series,
        #         trimType_=trim_type_element,
        #         flowCharacter_=flow_charac_element,
        #         flowDirection_=flow_direction_element,
        #         balancing_=balancing_element,
        #         rating_c=rating_element,
        #         style=v_style_element
        #     )
        #     db.session.add(new_cv_table_entry)
        #     db.session.commit()

    # Once data added, input all cv values
    all_cvs = cvTable.query.all()
    db.session.commit()
    
    print(len(all_cvs))
    for cv_index in range(len(all_cvs)):
        # CV value from excel
        new_cv_values_cv = cvValues(
            coeff=data_list[cv_index * 4]['coeff'],
            seatBore=float(data_list[cv_index * 4]['seatBore']),
            travel=float(data_list[cv_index * 4]['travel']),
            cv=all_cvs[cv_index],
            one=float(data_list[cv_index * 4]['one']),
            two=float(data_list[cv_index * 4]['two']),
            three=float(data_list[cv_index * 4]['three']),
            four=float(data_list[cv_index * 4]['four']),
            five=float(data_list[cv_index * 4]['five']),
            six=float(data_list[cv_index * 4]['six']),
            seven=float(data_list[cv_index * 4]['seven']),
            eight=float(data_list[cv_index * 4]['eight']),
            nine=float(data_list[cv_index * 4]['nine']),
            ten=float(data_list[cv_index * 4]['ten'])
        )

        # Fl Value from excel
        new_cv_values_fl = cvValues(
            coeff=data_list[cv_index * 4 + 1]['coeff'],
            seatBore=float(data_list[cv_index * 4 + 1]['seatBore']),
            travel=float(data_list[cv_index * 4 + 1]['travel']),
            cv=all_cvs[cv_index],
            one=float(data_list[cv_index * 4 + 1]['one']),
            two=float(data_list[cv_index * 4 + 1]['two']),
            three=float(data_list[cv_index * 4 + 1]['three']),
            four=float(data_list[cv_index * 4 + 1]['four']),
            five=float(data_list[cv_index * 4 + 1]['five']),
            six=float(data_list[cv_index * 4 + 1]['six']),
            seven=float(data_list[cv_index * 4 + 1]['seven']),
            eight=float(data_list[cv_index * 4 + 1]['eight']),
            nine=float(data_list[cv_index * 4 + 1]['nine']),
            ten=float(data_list[cv_index * 4 + 1]['ten'])
        )

        # Xt value from excel
        new_cv_values_xt = cvValues(
            coeff=data_list[cv_index * 4 + 2]['coeff'],
            seatBore=float(data_list[cv_index * 4 + 2]['seatBore']),
            travel=float(data_list[cv_index * 4 + 2]['travel']),
            cv=all_cvs[cv_index],
            one=float(data_list[cv_index * 4 + 2]['one']),
            two=float(data_list[cv_index * 4 + 2]['two']),
            three=float(data_list[cv_index * 4 + 2]['three']),
            four=float(data_list[cv_index * 4 + 2]['four']),
            five=float(data_list[cv_index * 4 + 2]['five']),
            six=float(data_list[cv_index * 4 + 2]['six']),
            seven=float(data_list[cv_index * 4 + 2]['seven']),
            eight=float(data_list[cv_index * 4 + 2]['eight']),
            nine=float(data_list[cv_index * 4 + 2]['nine']),
            ten=float(data_list[cv_index * 4 + 2]['ten'])
        )

        # Fd value from excel
        new_cv_values_fd = cvValues(
            coeff=data_list[cv_index * 4 + 3]['coeff'],
            seatBore=float(data_list[cv_index * 4 + 3]['seatBore']),
            travel=float(data_list[cv_index * 4 + 3]['travel']),
            cv=all_cvs[cv_index],
            one=float(data_list[cv_index * 4 + 3]['one']),
            two=float(data_list[cv_index * 4 + 3]['two']),
            three=float(data_list[cv_index * 4 + 3]['three']),
            four=float(data_list[cv_index * 4 + 3]['four']),
            five=float(data_list[cv_index * 4 + 3]['five']),
            six=float(data_list[cv_index * 4 + 3]['six']),
            seven=float(data_list[cv_index * 4 + 3]['seven']),
            eight=float(data_list[cv_index * 4 + 3]['eight']),
            nine=float(data_list[cv_index * 4 + 3]['nine']),
            ten=float(data_list[cv_index * 4 + 3]['ten'])
        )

        # Add object in a single session
        objects_list = [new_cv_values_cv, new_cv_values_fl, new_cv_values_xt, new_cv_values_fd]
        db.session.add_all(objects_list)
        db.session.commit()

    print("Data Upload CV End")


def deleteCVDuplicates():
    all_cvs = cvTable.query.all()
    # for cv in all_cvs:
    #     trim_type_element = db.session.query(trimType).filter_by(
    #         name=cv.trimType_.name).first()
    #     flow_charac_element = db.session.query(flowCharacter).filter_by(
    #         name=cv.flowCharacter_.name).first()
    #     flow_direction_element = db.session.query(flowDirection).filter_by(
    #         name=cv.flowDirection_.name).first()
    #     balancing_element = db.session.query(balancing).filter_by(
    #         name=cv.balancing_.name).first()
    #     rating_element = db.session.query(ratingMaster).filter_by(
    #         name=cv.rating_c.name).first()
    #     v_style_element = db.session.query(valveStyle).filter_by(name=cv.style.name).first()
    #     valve_size = float(cv.valveSize)
        
        
    #     cv__lists = db.session.query(cvTable).filter_by(trimType_=trim_type_element, flowCharacter_=flow_charac_element, flowDirection_=flow_direction_element, rating_c=rating_element, style=v_style_element, balancing_=balancing_element, valveSize=valve_size).all()
    #     if len(cv__lists) > 1:
    #         for data__ in cv__lists[1:]:
    #             data_element = db.session.query(cvTable).filter_by(id=data__.id).first()
    #             db.session.delete(data_element)
    #             db.session.commit()

    # print(len(all_cvs))
    # print(all_cvs[985:])
    print('Delete extra CV')
    if len(all_cvs) > 982:
        for cv_ in all_cvs[982:]:
            data_element = db.session.query(cvTable).filter_by(id=cv_.id).first()
            db.session.delete(data_element)
            db.session.commit()
    print('Delete Extra CV End')
    all_cvs_new = cvTable.query.all()
    print(f'{len(all_cvs_new)}')


def data_upload_disc_seat_packing(data_list, valve_style, table_name):
   
    data_delete(table_name)
    print("Data Upload Starts")
    for style_index in range(len(valve_style)):
        for data in data_list[style_index]:
            new_data = table_name(name=data, style=valve_style[style_index])
            db.session.add(new_data)
            db.session.commit()
    print("Data Upload Ends")

def data_upload_shaft(data_list, v_style_list):
    print('Shaft data add start')
    data_delete(shaft)
    all_elements = []
    for style_ in v_style_list:
        for data_ in data_list:
            new_shaft = shaft(name=data_['name'], yield_strength=data_['yield_strength'], style=style_)
            # all_elements.append(new_shaft)

            db.session.add(new_shaft)
            db.session.commit()


def addProjectRels(cname, cnameE, address, addressE, aEng, cEng, project, operation):
    # with app.app_context():
    company_element = db.session.query(companyMaster).filter_by(name=cname).first()
    company_element_E = db.session.query(companyMaster).filter_by(name=cnameE).first()
    company_address_element = db.session.query(addressMaster).filter_by(address=address,
                                                                        company=company_element).first()
    company_address_element_E = db.session.query(addressMaster).filter_by(address=addressE,
                                                                            company=company_element_E).first()
    aEng_ = engineerMaster.query.get(int(aEng))
    cEng_ = engineerMaster.query.get(int(cEng))
    if operation == 'create':
        # Add Engineers
        new_addr_project_company = addressProject(isCompany=True, address=company_address_element, project=project)
        new_addr_project_enduser = addressProject(isCompany=False, address=company_address_element_E, project=project)
        # Add Addresses
        new_er_project_application = engineerProject(isApplication=True, engineer=aEng_, project=project)
        new_er_project_contract = engineerProject(isApplication=False, engineer=cEng_, project=project)

        db.session.add_all(
            [new_addr_project_company, new_addr_project_enduser, new_er_project_application, new_er_project_contract])
        db.session.commit()
    elif operation == 'update':
        address_element_c = db.session.query(addressProject).filter_by(isCompany=True, project=project).first()
        address_element_e = db.session.query(addressProject).filter_by(isCompany=False, project=project).first()
        er_app = db.session.query(engineerProject).filter_by(isApplication=True, project=project).first()
        er_contr = db.session.query(engineerProject).filter_by(isApplication=False, project=project).first()

        if address_element_c and address_element_e and er_app and er_contr:
            address_element_c.address = company_address_element
            address_element_e.address = company_address_element_E
            er_app.engineer = aEng_
            er_contr.engineer = cEng_
            print(address_element_c.address, address_element_e.address, er_app.engineer, er_contr.engineer)
            db.session.commit()
        else:
            # Add Engineers
            new_addr_project_company = addressProject(isCompany=True, address=company_address_element, project=project)
            new_addr_project_enduser = addressProject(isCompany=False, address=company_address_element_E,
                                                        project=project)
            # Add Addresses
            new_er_project_application = engineerProject(isApplication=True, engineer=aEng_, project=project)
            new_er_project_contract = engineerProject(isApplication=False, engineer=cEng_, project=project)

            db.session.add_all([new_addr_project_company, new_addr_project_enduser, new_er_project_application,
                                new_er_project_contract])
            db.session.commit()


def addUserAsEng(name, designation):
    # with app.app_context():
    new_engineer = engineerMaster(name=name, designation=designation)
    db.session.add(new_engineer)
    db.session.commit()


def newUserProjectItem(user):
# with app.app_context():
    fluid_state = fluidState.query.first()
    new_project = projectMaster(user=user,
                                projectId=f"Q{date_today[2:4]}0000",
                                enquiryReceivedDate=datetime.datetime.today(),
                                receiptDate=datetime.datetime.today(),
                                bidDueDate=datetime.datetime.today())
    new_item = itemMaster(project=new_project, itemNumber=1, alternate='A')
    new_valve = valveDetailsMaster(item=new_item, state=fluid_state)
    new_actuator = actuatorMaster(item=new_item)
    new_accessories = accessoriesData(item=new_item)
    db.session.add_all([new_project, new_item, new_valve, new_actuator, new_accessories])
    db.session.commit()


def newProjectItem(project):
    fluid_state = fluidState.query.first()
    new_item = itemMaster(project=project, itemNumber=1, alternate='A')
    db.session.add(new_item)
    db.session.commit()
    new_valve_det = valveDetailsMaster(item=new_item, state=fluid_state)
    db.session.add(new_valve_det)
    db.session.commit()
    new_actuator = actuatorMaster(item=new_item)
    db.session.add(new_actuator)
    db.session.commit()
    new_accessories = accessoriesData(item=new_item)
    db.session.add(new_accessories)
    db.session.commit()
    return new_item

# def newProjectItemCopy(project):
#     fluid_state = fluidState.query.first()
#     new_item = itemMaster(project=project, itemNumber=1, alternate='A')
#     db.session.add(new_item)
#     db.session.commit()
#     new_valve_det = valveDetailsMaster(item=new_item, state=fluid_state)
#     db.session.add(new_valve_det)
#     db.session.commit()
#     new_actuator = actuatorMaster(item=new_item)
#     db.session.add(new_actuator)
#     db.session.commit()
#     new_accessories = accessoriesData(item=new_item)
#     db.session.add(new_accessories)
#     db.session.commit()
#     return new_item


def addNewItem(project, itemNumber, alternate):
    # with app.app_context():
    fluid_state = fluidState.query.first()
    new_item = itemMaster(project=project, itemNumber=itemNumber, alternate=alternate)
    db.session.add(new_item)
    db.session.commit()
    new_valve_det = valveDetailsMaster(item=new_item, state=fluid_state)
    db.session.add(new_valve_det)
    db.session.commit()
    new_actuator = actuatorMaster(item=new_item)
    db.session.add(new_actuator)
    db.session.commit()
    new_actuator_case = actuatorCaseData(actuator_=new_actuator)
    db.session.add(new_actuator_case)
    db.session.commit()
    new_rotary_case = rotaryCaseData(actuator_=new_actuator)
    db.session.add(new_rotary_case)
    db.session.commit()
    new_stroke_case = strokeCase(actuatorCase_=new_actuator_case,status=1)
    db.session.add(new_stroke_case)
    db.session.commit()
    new_accessories = accessoriesData(item=new_item)
    db.session.add(new_accessories)
    db.session.commit()
    return new_item

def addNewItemAlternate(project, itemNumber, alternate, valveElement):
    # with app.app_context():
    fluid_state = fluidState.query.first()
    new_item = itemMaster(project=project, itemNumber=itemNumber, alternate=alternate, standardStatus=valveElement.item.standardStatus, pipeDataStatus=valveElement.item.pipeDataStatus)
    db.session.add(new_item)
    db.session.commit()
    new_valve_det = valveDetailsMaster(item=new_item, state=valveElement.state)
    for attr in inspect(valveElement).attrs:
        # print(attr.key)
        # print(type(attr.key))
        if attr.key not in ['id', 'itemId', 'fluidStateId', 'item', 'state']:
            print(attr.key)
            setattr(new_valve_det, attr.key, getattr(valveElement, attr.key))
        # setattr(new_valve_det, 'itemId', getattr(valveElement, 'itemId'))
    db.session.add(new_valve_det)
    db.session.commit()
    # Cases:
    cases_ = db.session.query(caseMaster).filter_by(item=valveElement.item).all()
    for case__ in cases_:
        new_case = caseMaster(item=new_item)
        for attr in inspect(case__).attrs:
            if attr.key not in ['id', 'itemId', 'item']:
                setattr(new_case, attr.key, getattr(case__, attr.key))
        db.session.add(new_case)
        db.session.commit()
    new_actuator = actuatorMaster(item=new_item)
    db.session.add(new_actuator)
    db.session.commit()
    new_actuator_case = actuatorCaseData(actuator_=new_actuator)
    db.session.add(new_actuator_case)
    db.session.commit()
    new_accessories = accessoriesData(item=new_item)
    db.session.add(new_accessories)
    db.session.commit()
    return new_item


# def checkAddNewValve():
#     item_ = itemMaster.query.first()
#     old_valve_data = db.session.query(valveDetailsMaster).filter_by(item=item_).first()
#     print(item_.id, old_valve_data.id)
#     new_valve_det = valveDetailsMaster(item=item_, state=old_valve_data.state)
#     for attr in inspect(old_valve_data).attrs:
#         # print(attr.key)
#         if attr.key not in ['id', 'itemId', 'fluidStateId']:
#             setattr(new_valve_det, attr.key, getattr(old_valve_data, attr.key))
#     db.session.add(new_valve_det)
#     db.session.commit()

# with app.app_context():
#     checkAddNewValve()
# TODO Functional Module
# def sendOTP(username):
#     # Generate Random INT
#     random_decimal = random.random()
#     random_int = round(random_decimal * 10 ** 6)
#     otp__ = db.session.query(OTP).filter_by(username=username).all()
#     if len(otp__) == 0:
#         new_otp = OTP(otp=random_int, username=username, time=datetime.datetime.now())
#         db.session.add(new_otp)
#         db.session.commit()
#     else:
#         otp_1 = db.session.query(OTP).filter_by(username=username).first()
#         otp_1.otp = random_int
#         otp_1.time = datetime.datetime.now()
#         db.session.commit()
    
#     # try:
#     # Send email
#     s = smtplib.SMTP('smtp.gmail.com', 587)
#     # s.ehlo()
#     s.starttls()
#     # s.ehlo()
#     sender_email = 'titofccvs@gmail.com'
#     sender_email_password = 'lvcf senp padh csyr'
#     # sender_email_password = 'titofccvs@2023'
#     reciever_email = ['kartheeswaran1707v@gmail.com', username]
#     s.login(sender_email, sender_email_password)
#     # message = f"The OTP for resetting password is: {random_int}"
#     message = "OTP for Reset Password is " + str(random_int)
#     print(message)
#     s.sendmail(sender_email, reciever_email, message)
#     s.quit()
#     mail_sent = True
#     # except Exception as e:
#     #     print(f'Mail Issue {e}')
#     #     mail_sent = False
#     # msg = MIMEMultipart()
#     # msg['From'] = sender_email
#     # msg['To'] = reciever_email
#     # msg['Subject'] = 'OTP for Reset Password'
#     # message = f"The OTP for resetting password is: {random_int}"
#     # msg.attach(MIMEText(message))

#     # with smtplib.SMTP('smtp-mail.outlook.com',587) as mail_server:
#     #     # identify ourselves to smtp gmail client
#     #     # secure our email with tls encryption
#     #     mail_server.starttls()
#     #     # re-identify ourselves as an encrypted connection
#     #     # mail_server.ehlo()
#     #     mail_server.login(sender_email, sender_email_password)
#     #     mail_server.sendmail(sender_email, reciever_email, message)
#     return mail_sent

def sendOTP(username):
    # Generate Random INT
    random_decimal = random.random()
    random_int = round(random_decimal * 10 ** 6)
    otp__ = db.session.query(OTP).filter_by(username=username).all()
    if len(otp__) == 0:
        new_otp = OTP(otp=random_int, username=username, time=datetime.datetime.now())
        db.session.add(new_otp)
        db.session.commit()
    else:
        otp_1 = db.session.query(OTP).filter_by(username=username).first()
        otp_1.otp = random_int
        otp_1.time = datetime.datetime.now()
        db.session.commit()
    try:
        # Send email using Hostinger's SMTP server
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        sender_email = 'fccommuneit@gmail.com'  # Replace with your Hostinger email
        sender_email_password = 'reuk tgqf ftyi mrsx'  # Replace with your Hostinger email password
        # sender_email = 'sizinghelp@valvesizing.fccommune.com'  # Replace with your Hostinger email
        # sender_email_password = 'Sizing@admin0'  # Replace with your Hostinger email password
        reciever_email = ['pandi709410@gmail.com', username]

        # Login to the SMTP server
        s.login(sender_email, sender_email_password)

        # Construct the email message
        message = f"Subject: OTP for Create Password\n\n"
        message += f"OTP for Create Password is {random_int}"
        print(random_int)
        # Send the email
        s.sendmail(sender_email, reciever_email, message)
        print(reciever_email)
        # Close the connection to the SMTP server
        s.quit()

        # Set mail_sent flag to indicate successful email sending
        mail_sent = True
    except Exception as e:
        print(f'Failed to send OTP email: {e}')
        # Set mail_sent flag to indicate failure
        mail_sent = False
    return mail_sent

def getEngAddrList(all_projects):
    address_ = []
    eng_ = []
    for project in all_projects:
        address_c = db.session.query(addressProject).filter_by(project=project, isCompany=True).first()
        eng_a = db.session.query(engineerProject).filter_by(project=project, isApplication=False).first()
        address_.append(address_c)
        eng_.append(eng_a)
    return address_, eng_


def getEngAddrProject(project):
    address_c = db.session.query(addressProject).filter_by(project=project, isCompany=True).first()
    address_e = db.session.query(addressProject).filter_by(project=project, isCompany=False).first()
    eng_a = db.session.query(engineerProject).filter_by(project=project, isApplication=True).first()
    eng_c = db.session.query(engineerProject).filter_by(project=project, isApplication=False).first()
    return address_c, address_e, eng_a, eng_c


def getDBElementWithId(table_name, id):
    # with app.app_context():
    if id:
        output_element = db.session.query(table_name).filter_by(id=id).first()
        return output_element
    else:
        return None

def getDBElementWithName(table_name, name):
    if name:
    # with app.app_context():
        output_element = db.session.query(table_name).filter_by(name=name).first()
        return output_element
    else:
        return None

def float_convert(input_):
    try:
        output_ = float(input_)
    except:
        output_ = None
    return output_


date_today = datetime.datetime.now().strftime("%Y-%m-%d")


def fluid_properties_dict_vs():
    with app.app_context():
        fluids = fluidProperties.query.all()
        keys_ = fluidProperties.__table__.columns.keys()
        print(keys_)
        fl_dict = {}
        for fl_ in fluids:
            fl_dict[fl_.fluidName] = {}
            for key_ in keys_[3:]:
                fl_dict[fl_.fluidName][key_] = getattr(fl_, key_)


        return fl_dict


def metadata():
    with app.app_context():
        globe_element_1 = db.session.query(valveStyle).filter_by(name="Globe Straight").first()
        butterfly_element_1 = db.session.query(valveStyle).filter_by(name="Butterfly Lugged Wafer").first()
        companies = companyMaster.query.all()
        industries = industryMaster.query.all()
        regions = regionMaster.query.all()
        engineers = engineerMaster.query.all()
        ratings = ratingMaster.query.all()
        bodyMaterial = materialMaster.query.all()
        standard_ = designStandard.query.all()
        valveStyles = valveStyle.query.all()
        endconnection = endConnection.query.all()
        endfinish = endFinish.query.all()
        bonnettype = bonnetType.query.all()
        packingtype = packingType.query.all()
        trimtype = trimType.query.all()
        flowcharacter = flowCharacter.query.all()
        flowdirection = flowDirection.query.all()
        flowCharacter_ = flowCharacter.query.all()
        seatleakageclass = seatLeakageClass.query.all()
        bonnet_ = bonnet.query.all()
        shaft_ = shaft.query.all()
        disc_ = disc.query.all()
        seat_ = seat.query.all()
        packing_ = packing.query.all()
        balanceseal = balanceSeal.query.all()
        balancing_ = balancing.query.all()
        studnut = studNut.query.all()
        gasket_ = gasket.query.all()
        cageclamp = cageClamp.query.all()
        application_ = applicationMaster.query.all()
        fluids = fluidProperties.query.all()
        fluids_dict = fluid_properties_dict_vs()
        fluid_state = fluidState.query.all()
        valveSeries = []
        for notes_ in db.session.query(cvTable.series).distinct():
            valveSeries.append(notes_.series)

        notes_dict = {}
        for nnn in companies:
            contents = db.session.query(addressMaster).filter_by(company=nnn, isActive=True).all()
            content_list = [cont.address for cont in contents]
            notes_dict[nnn.name] = content_list

        data_dict = {
            "companies": companies,
            "industries": industries,
            "regions": regions,
            "engineers": engineers,
            "notes_dict": json.dumps(notes_dict),
            "fluids_dict": json.dumps(fluids_dict),
            "notes_dict_": notes_dict,
            "status": project_status_list,
            "date": date_today,
            "purpose": purpose_list,
            "ratings": ratings,
            "bodyMaterial": bodyMaterial,
            "standard": standard_,
            "valveStyle": valveStyles,
            "valveSeries": valveSeries,
            "endconnection": endconnection,
            "endfinish": endfinish,
            "bonnettype": bonnettype,
            "packingtype": packingtype,
            "trimtype": trimtype,
            "flowcharacter": flowcharacter,
            "flowdirection": flowdirection,
            "seatleakageclass": seatleakageclass,
            "bonnet": bonnet_,
            "shaft": shaft_,
            "disc": disc_,
            "seat": seat_,
            "packing": packing_,
            "balanceseal": balanceseal,
            "studnut": studnut,
            "gasket": gasket_,
            "cageclamp": cageclamp,
            "application": application_,
            "units_dict": units_dict,
            "fluids": fluids,
            "fluidState": fluid_state,
            "flowCharacter": flowCharacter_,
            "actuatorData": actuator_data_dict,
            "globeStyleId": int(globe_element_1.id),
            "butterflyStyleId": int(butterfly_element_1.id),
            "balancing":balancing_
        }

        positioner_manufacturer = []
        for notes_ in db.session.query(positioner.manufacturer).distinct():
            positioner_manufacturer.append(notes_.manufacturer)

        positioner_model = []
        for notes_ in db.session.query(positioner.series).distinct():
            positioner_model.append(notes_.series)

        positioner_action = []
        for notes_ in db.session.query(positioner.action).distinct():
            positioner_action.append(notes_.action)
        
        solenoid_make = []
        for notes_ in db.session.query(solenoid.make).distinct():
            solenoid_make.append(notes_.make)

        solenoid_model = []
        for notes_ in db.session.query(solenoid.model).distinct():
            solenoid_model.append(notes_.model)

        solenoid_type = []
        for notes_ in db.session.query(solenoid.type).distinct():
            solenoid_type.append(notes_.type)

        all_afr = afr.query.all()
        afr_ = [f"{pos.manufacturer}/{pos.model}" for pos in all_afr]

        all_limit_switch = limitSwitch.query.all()
        limit_switch_ = [l.model for l in all_limit_switch]
        
        data_dict['positioner_manufacturer'] = positioner_manufacturer
        data_dict['positioner_model'] = positioner_model
        data_dict['positioner_action'] = positioner_action
        data_dict['afr_'] = afr_
        data_dict['limit_switch_'] = limit_switch_
        data_dict['solenoid_make'] = solenoid_make
        data_dict['solenoid_model'] = solenoid_model
        data_dict['solenoid_type'] = solenoid_type
        data_dict['boosters'] = ['I-BP1A', 'W20359']
        return data_dict


# TODO ------------------------------------------ SIZING PYTHON CODE --------------------------------------- #


# Cv1 = Cv_butterfly_6
# FL1 = Fl_butterfly_6


# TODO - Liquid Sizing - fisher
def etaB(valveDia, pipeDia):
    return 1 - ((valveDia / pipeDia) ** 4)


def eta1(valveDia, pipeDia):
    return 0.5 * ((1 - ((valveDia / pipeDia) ** 2)) ** 2)


def eta2(valveDia, pipeDia):
    return 1 * ((1 - ((valveDia / pipeDia) ** 2)) ** 2)


def sigmaEta(valveDia, inletDia, outletDia):
    a_ = eta1(valveDia, inletDia) + eta2(valveDia, outletDia) + etaB(valveDia, inletDia) - etaB(valveDia, outletDia)
    # print(
    #     f"sigma eta inputs: {eta1(valveDia, inletDia)}, {eta2(valveDia, outletDia)}, {etaB(valveDia, inletDia)}, {valveDia}, {outletDia}")
    return a_


def FF(vaporPressure, criticalPressure):
    a = 0.96 - 0.28 * math.sqrt(vaporPressure / criticalPressure)
    return a


def fP(C, valveDia, inletDia, outletDia, N2_value):
    a = (sigmaEta(valveDia, inletDia, outletDia) / N2_value) * ((C / valveDia ** 2) ** 2)
    print(
        f"fp numerator: {a}, n2 value: {N2_value}, valveDia: {valveDia}, sigmaeta: {sigmaEta(valveDia, inletDia, outletDia)}, CV: {C}")
    print(f"Sigma eta: {sigmaEta(valveDia, inletDia, outletDia)}")
    b_ = 1 / math.sqrt(1 + round(a,3))
    # return 0.71
    return round(b_, 3)
    # return 0.98


def flP(C, valveDia, inletDia, N2_value, Fl):
    K1 = eta1(valveDia, inletDia) + etaB(valveDia, inletDia)
    # print(f"k1, valvedia, inlet, C: {K1}, {valveDia}, {inletDia}, {N2_value}, {Fl}, {C}")
    a = (K1 / N2_value) * ((C / valveDia ** 2) ** 2)
    # print(f"a for flp: {a}")
    try:
        b_ = 1 / math.sqrt((1 / (Fl * Fl)) + a)
    except:
        b_ = 0.9
    return round(b_, 3)


def delPMax(Fl, Ff, inletPressure, vaporPressure):
    a_ = Fl * Fl * (inletPressure - (Ff * vaporPressure))
    # print(f"delpmax: {Fl}, {inletPressure}, {Ff}, {vaporPressure}")
    return round(a_, 3)


def selectDelP(Fl, criticalPressure, inletPressure, vaporPressure, outletPressure):
    Ff = FF(vaporPressure, criticalPressure)
    a_ = delPMax(Fl, Ff, inletPressure, vaporPressure)
    b_ = inletPressure - outletPressure
    # print(f"delpmax: {a_} and delP: {b_}")
    return min(a_, b_)


def Cvt(flowrate, N1_value, inletPressure, outletPressure, sGravity):
    a_ = N1_value * math.sqrt((inletPressure - outletPressure) / sGravity)
    b_ = flowrate / a_
    # print(f"CVt: {b_}")
    return round(b_, 3)


def reynoldsNumber(N4_value, Fd, flowrate, viscosity, Fl, N2_value, pipeDia, N1_value, inletPressure, outletPressure,
                   sGravity):
    Cv_1 = Cvt(flowrate, N1_value, inletPressure, outletPressure, sGravity)
    # print(Cv_1)
    a_ = (N4_value * Fd * flowrate) / (viscosity * math.sqrt(Fl * Cv_1))
    # print(a_)
    b_ = ((Fl * Cv_1) ** 2) / (N2_value * (pipeDia ** 4))
    c_ = (1 + b_) ** (1 / 4)
    d_ = a_ * c_
    return round(d_, 3)


def getFR(N4_value, Fd, flowrate, viscosity, Fl, N2_value, pipeDia, N1_value, inletPressure, outletPressure, sGravity):
    RE = reynoldsNumber(N4_value, Fd, flowrate, viscosity, Fl, N2_value, pipeDia, N1_value, inletPressure,
                        outletPressure, sGravity)
    # print(RE)
    if 56 <= RE <= 40000:
        a = 0
        while True:
            # print(f"Cv1, C: {Cv1[a], C}")
            if REv[a] == RE:
                return FR[a]
            elif REv[a] > RE:
                break
            else:
                a += 1

        fr = FR[a - 1] - (((REv[a - 1] - RE) / (REv[a - 1] - REv[a])) * (FR[a - 1] - FR[a]))

        return round(fr, 3)
    elif RE < 56:
        a = 0.019 * (RE ** 0.67)
        return a
    else:
        return 1


# print(7600, 1, 300, 8000, 0.68, 0.00214, 80, 0.865, 8.01, 6.01, 0.908)


def CV(flowrate, C, valveDia, inletDia, outletDia, N2_value, inletPressure, outletPressure, sGravity, N1_value, Fd,
       vaporPressure, Fl, criticalPressure, N4_value, viscosity, thickness):
    if valveDia != inletDia:
        FLP = flP(C, valveDia, inletDia + 2 * thickness, N2_value, Fl)
        FP = fP(C, valveDia, inletDia + 2 * thickness, outletDia + 2 * thickness, N2_value)
        print(f"FPSSSSSSSSSSS: {FLP},{FP}")
        FL = FLP / FP
    else:
        FL = Fl
    delP = selectDelP(FL, criticalPressure, inletPressure, vaporPressure, outletPressure)
    Fr = getFR(N4_value, Fd, flowrate, viscosity, FL, N2_value, inletDia + 2 * thickness, N1_value, inletPressure,
               outletPressure,
               sGravity)
    # print(Fr)
    fp_val = fP(C, valveDia, inletDia + 2 * thickness, outletDia + 2 * thickness, N2_value)
    print(delP, sGravity)
    a_ = N1_value * fp_val * Fr * math.sqrt(delP / sGravity)
    print(N1_value, fp_val, Fr, delP)
    b_ = flowrate / a_
    # print(f"FR: {Fr}")
    return round(b_, 3)

### --------------------------------- Routes -----------------------------------------------------###

def getUniqueValues(table_name):
    empty_list = []
    for notes_ in db.session.query(table_name.name).distinct():
        empty_list.append({"id": notes_.id, "name": notes_.name})
    return empty_list


# TODO Login Module
@app.route('/email-otp', methods=["GET", "POST"])
def emailOTP():
    if request.method == 'POST':
        email_ = request.form.get('email')
        # flash('Incorrect OTP1')
        otp_ = request.form['otp']
        # flash('Incorrect OTP2')
        print(f'otp_ {otp_}')
        otp_element = db.session.query(OTP).filter_by(username=email_).first()
        # flash('Incorrect OTP3')
        if int(otp_element.otp) == int(otp_):
            # flash('Correct OTP')
            # print(f'correct OTP _______')
            session['email'] = email_
            return redirect(url_for('register'))
        else:
            flash('Incorrect OTP')
            return render_template("email-otp.html", default_email=email_)
           
    return render_template("email-otp.html", default_email='')



@app.route('/admin-register', methods=["GET", "POST"])
def register():
    email = session.get('email')
    designations_ = designationMaster.query.all()
    
    departments_ = departmentMaster.query.all()
    if request.method == "POST":

        if userMaster.query.filter_by(email=request.form['email']).first():
            # user already exists
            flash("Email-ID already exists")
            return redirect(url_for('register', email=email))
        else:
            department_element = departmentMaster.query.get(int(request.form['department']))
            designation_element = designationMaster.query.get(int(request.form['designation']))
            new_user = userMaster(email=request.form['email'],
                                  password=generate_password_hash(request.form['password'], method='pbkdf2:sha256',
                                                                  salt_length=8),
                                  name=request.form['name'],
                                  employeeId=None,
                                  mobile=request.form['mobile'],
                                  designation=designation_element,
                                  department=department_element,
                                  fccUser=True
                                  )
            db.session.add(new_user)
            db.session.commit()

            if department_element.name == "Application Engineering, Sales & Contracts":
                addUserAsEng(request.form['name'], designation_element.name)

            # Add Project and Item
            newUserProjectItem(user=new_user)
            # login_user(new_user)
            # flash('Logged in successfully.')
            return redirect(url_for('login'))

    return render_template("admin-registration.html", email=email, designations=designations_, departments=departments_)


@app.route('/', methods=["GET", "POST"])
def login():
    # form = LoginForm()
    if request.method == "POST":

        user = userMaster.query.filter_by(email=request.form['email']).first()

        # email doesn't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))

        # Password incorrect
        elif not check_password_hash(user.password, request.form['password']):
            flash("Password incorrect, please try again.")
            return redirect(url_for('login'))

        # email exists and password correct
        else:
            login_user(user)
            project_element = db.session.query(projectMaster).filter_by(user=user).first()
            item_element = db.session.query(itemMaster).filter_by(project=project_element).first()
            return redirect(url_for('home', proj_id=project_element.id, item_id=item_element.id))

    return render_template("login.html")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/reset-pw', methods=["GET", "POST"])
def resetPassword():
    if request.method == 'POST':
        email_ = request.form.get('email')
        is_mail_sent = sendOTP(email_)
        if is_mail_sent:
            session['reset-email'] = email_
            return redirect(url_for('sendOTPEmail'))
        else:
            flash('Something went wrong')
            return redirect(url_for('resetPassword'))
    return render_template('send-email-otp.html')


@app.route('/send_otp', methods=["GET", "POST"])
def sendOTPAjax():
    print('function is called for otp')
    emailID = request.args.get('emailID')
    print(emailID)
    # emailID = request.form['emailID']
    if userMaster.query.filter_by(email=emailID).first():
        json_ = {'message': 'User already exist'}
    else:
        result_ = sendOTP(emailID)
        if result_:
            json_ = {'message': 'OTP Sent'}
        else:
            json_ = {'message': 'Something Went Wrong'}
    return jsonify(json_)

@app.route('/send-otp', methods=["GET", "POST"])
def sendOTPEmail():
    email = session.get('reset-email')
    if request.method == 'POST':
        otp_ = request.form['otp']
        username = email
        otp_element = db.session.query(OTP).filter_by(username=username).first()
        if int(otp_element.otp) == int(otp_):
            user_element = db.session.query(userMaster).filter_by(email=username).first()
            user_element.password = generate_password_hash(request.form['password'], method='pbkdf2:sha256',
                                                                  salt_length=8)
            db.session.commit()
            flash('Password Reset Successfully')
            return redirect(url_for('login'))
        else:
            flash('Incorrect OTP')
    return render_template('reset-pw.html', email=email)


# TODO Dashboard Module

@app.route('/home/proj-<proj_id>/item-<item_id>', methods=['GET'])
def home(proj_id, item_id):
    item_element = itemMaster.query.get(int(item_id))
    all_projects = db.session.query(projectMaster).filter_by(user=current_user).all()
    address_, eng_ = getEngAddrList(all_projects)
    items_list = db.session.query(itemMaster).filter_by(project=projectMaster.query.get(int(proj_id))).order_by(
        itemMaster.itemNumber.asc()).all()
    valve_list = [db.session.query(valveDetailsMaster).filter_by(item=item_).first() for item_ in items_list]
    valve_size_list = []
    model_list = []
    for valve_ in valve_list:
        try:
            cases_ = db.session.query(caseMaster).filter_by(item=valve_.item).first()
            if cases_:
                if cases_.cv:
                    valve_size = cases_.cv.valveSize
                    model_ = getModelValve(cases_.cv.series, valve_.rating.name, valve_.trimType__.name, valve_.maxTemp, valve_.seat__.name, valve_.balanceSeal__.name, valve_.item.intemp_unit)
                    model_list.append(model_)
                else:
                    valve_size = None
                    model_list.append(None)
            else:
                valve_size = None
                model_list.append(None)
            valve_size_list.append(valve_size)
        except:
            model_list.append(None)
            valve_size_list.append(None)

    # for valve_ in range(len(valve_list)):
    #     if not valve_list[valve_]:
    #         new_valve = valveDetailsMaster(item=items_list[valve_], state=fluidState.query.first())
    #         db.session.add(new_valve)
    #         db.session.commit()
    return render_template('dashboard.html', user=current_user, projects=all_projects, address=address_, eng=eng_,
                            item=item_element, items=valve_list, sizes=valve_size_list, models=model_list, page='home')


@app.route('/getItems/proj-<proj_id>', methods=['GET'])
def getItems(proj_id):
    items_list = db.session.query(itemMaster).filter_by(project=projectMaster.query.get(int(proj_id))).all()
    print(len(items_list))
    return redirect(url_for('home', proj_id=proj_id, item_id=items_list[0].id))


@app.route('/selectItem/item-<item_id>', methods=['GET'])
def selectItem(item_id):
    item_ = itemMaster.query.get(int(item_id))
    return redirect(url_for('home', proj_id=item_.project.id, item_id=item_.id))


@app.route('/add-item/proj-<proj_id>/item-<item_id>', methods=['GET'])
def addItem(proj_id, item_id):
    item_element = getDBElementWithId(itemMaster, item_id)
    project_element = getDBElementWithId(projectMaster, item_element.project.id)
    all_items = db.session.query(itemMaster).filter_by(project=project_element).all()
    last_item = all_items[-1]
    itemNumberCurrent = int(last_item.itemNumber) + 1
    print(f"last item number + 1 = {int(last_item.itemNumber) + 1}")
    addNewItem(project=project_element, itemNumber=itemNumberCurrent, alternate='A')
    return redirect(url_for('home', proj_id=proj_id, item_id=item_id))


@app.route('/add-alternate/proj-<proj_id>/item-<item_id>', methods=['GET'])
def addAlternate(proj_id, item_id):
    item_element = getDBElementWithId(itemMaster, item_id)
    project_element = getDBElementWithId(projectMaster, item_element.project.id)
    n_items = db.session.query(itemMaster).filter_by(project=project_element, itemNumber=item_element.itemNumber).all()
    itemNumberCurrent = int(item_element.itemNumber)
    alternateCurrent = next_alpha(n_items[-1].alternate)
    valve_element = db.session.query(valveDetailsMaster).filter_by(item=item_element).first()
    addNewItemAlternate(project=project_element, itemNumber=itemNumberCurrent, alternate=alternateCurrent, valveElement=valve_element)
    return redirect(url_for('home', proj_id=proj_id, item_id=item_id))


@app.route('/copy-alternate/proj-<proj_id>/item-<item_id>', methods=['GET'])
def copyItem(proj_id, item_id):
    item_element = getDBElementWithId(itemMaster, item_id)
    project_element = getDBElementWithId(projectMaster, item_element.project.id)
    all_items = db.session.query(itemMaster).filter_by(project=project_element).all()
    last_item = all_items[-1]
    itemNumberCurrent = int(last_item.itemNumber) + 1
    valve_element = db.session.query(valveDetailsMaster).filter_by(item=item_element).first()
    addNewItemAlternate(project=project_element, itemNumber=itemNumberCurrent, alternate='A', valveElement=valve_element)
    return redirect(url_for('home', proj_id=proj_id, item_id=item_id))


# @app.route('/copy-alternate/proj-<proj_id>/item-<item_id>', methods=['GET'])
# def copyProject(proj_id, item_id):
#     project_element = projectMaster.query.get(int(proj_id))
#     new_project = projectMaster(user=current_user)
#     for attr in inspect(project_element).attrs:
#         # print(attr.key)
#         # print(type(attr.key))
#         # if attr.key not in ['id', 'itemId', 'fluidStateId', 'item', 'state']:
#         print(attr.key)
#         setattr(new_project, attr.key, getattr(project_element, attr.key))
#         # setattr(new_valve_det, 'itemId', getattr(valveElement, 'itemId'))
#     db.session.add(new_project)
#     db.session.commit()
#     return redirect(url_for('home', proj_id=new_project.id, item_id=item_id))




@app.route('/preferences/proj-<proj_id>/item-<item_id>/<page>', methods=['GET', 'POST'])
def preferences(proj_id, item_id, page):
    metadata_ = metadata()
    with app.app_context():
        return render_template('preferences.html', user=current_user, metadata=metadata_, item=getDBElementWithId(itemMaster, item_id), page=page)


@app.route('/updatePreferences/proj-<proj_id>/item-<item_id>/<page>', methods=['POST'])
def updatePreferences(proj_id, item_id, page):
    with app.app_context():

        item_selected = getDBElementWithId(itemMaster, item_id)
        itemCases_1 = db.session.query(caseMaster).filter_by(item=item_selected).all()
        for i in itemCases_1:
            db.session.delete(i)
            db.session.commit()

        item_element = getDBElementWithId(itemMaster, item_id)
        item_element.flowrate_unit = request.form['flowrateUnit']
        item_element.inpres_unit = request.form['pressureUnit']
        item_element.outpres_unit = request.form['pressureUnit']
        item_element.intemp_unit = request.form['temperatureUnit']
        item_element.vaporpres_unit = request.form['pressureUnit']
        item_element.criticalpres_unit = request.form['pressureUnit']
        item_element.inpipe_unit = request.form['lengthUnit']
        item_element.outpipe_unit = request.form['lengthUnit']
        item_element.valvesize_unit = request.form['lengthUnit']
        db.session.commit()

        return redirect(url_for(page, proj_id=proj_id, item_id=item_id))


# TODO Company Module

@app.route('/company-master/proj-<proj_id>/item-<item_id>', methods=['GET', 'POST'])
def addCompany(proj_id, item_id):
    all_company = companyMaster.query.all()
    addresses = addressMaster.query.all()
    len_all_addr = len(addresses)
    company_names = [company.name for company in all_company]
    if request.method == "POST":
        if request.form.get('addCompany'):
            name = request.form.get('name')
            description = request.form.get('description')
            if name in company_names:
                flash('Company already exists')
                return redirect(url_for('addCompany', item_id=item_id, proj_id=proj_id))
            else:
                new_company = companyMaster(name=name, description=description)
                db.session.add(new_company)
                db.session.commit()
                # Add Address
                new_address = addressMaster(address=request.form.get('address'), company=new_company,
                                        customerCode=full_format(len_all_addr), isActive=True)
                db.session.add(new_address)
                db.session.commit()

                flash(f"Company: {name} added successfully.")
                return redirect(url_for('addCompany', item_id=item_id, proj_id=proj_id))
            
        elif request.form.get('newAddressFunction'):
            print('route working')
            company_id = request.form.get('company_id')
            address = request.form.get('addressAdd')
            company_element = db.session.query(companyMaster).filter_by(name=company_id).first()
            new_address = addressMaster(address=address, company=company_element,
                                            customerCode=full_format(len_all_addr), isActive=True)
            db.session.add(new_address)
            db.session.commit()
            flash('Address added successfully')
            return redirect(url_for('addCompany', item_id=item_id, proj_id=proj_id))
        elif request.form.get('editAddress'):
            company_id = request.form.get('name1')
            address = request.form.get('address1')
            address_id = request.form.get('address_id')
            address_element = getDBElementWithId(addressMaster, int(address_id))
            address_element.address = address
            db.session.commit()
            flash('Address Edited successfully')
            return redirect(url_for('addCompany', item_id=item_id, proj_id=proj_id))
    return render_template('customer_master.html', companies=all_company, user=current_user,
                           item=getDBElementWithId(itemMaster, item_id), page='addCompany', addresses=addresses)


@app.route('/check-company-exists', methods=['GET', 'POST'])
def isCompanyExist(proj_id, item_id):
    pass

@app.route('/add-address/proj-<proj_id>/item-<item_id>', methods=['GET', 'POST'])
def addAddress(proj_id, item_id):
    addresses = addressMaster.query.all()
    len_all_addr = len(addresses)
    company_id = request.form.get('company_id')
    address = request.form.get('addressAdd')
    company_element = getDBElementWithId(companyMaster, int(company_id))
    new_address = addressMaster(address=request.form.get('address'), company=company_element,
                                    customerCode=full_format(len_all_addr), isActive=True)
    db.session.add(new_address)
    db.session.commit()
    flash('Address added successfully')
    return redirect(url_for('addCompany', item_id=item_id, proj_id=proj_id))


@app.route('/company-edit/proj-<proj_id>/item-<item_id>/<company_id>', methods=['GET', 'POST'])
def companyEdit(company_id, proj_id, item_id):
    company_element = companyMaster.query.get(company_id)
    addresses = db.session.query(addressMaster).filter_by(company=company_element).all()
    all_addresses = addressMaster.query.all()
    len_all_addr = len(all_addresses)
    len_addr = len(addresses)
    if request.method == 'POST':
        company_element.name = request.form.get('name')
        company_element.description == request.form.get('description')
        new_address = addressMaster(address=request.form.get('address'), company=company_element,
                                    customerCode=full_format(len_all_addr), isActive=True)
        db.session.add(new_address)
        db.session.commit()
        flash('Address added successfully')
        return redirect(url_for('companyEdit', company_id=company_element.id, item_id=item_id, proj_id=proj_id))
    return render_template('customer_master_edit.html', user=current_user, company=company_element, addresses=addresses,
                           addresses_len=range(len_addr), item=getDBElementWithId(itemMaster, item_id), page='companyEdit')


@app.route('/del-address/<address_id>/proj-<proj_id>/item-<item_id>', methods=['GET', 'POST'])
def delAddress(address_id, item_id, proj_id):
    addresss_element = addressMaster.query.get(address_id)
    company_id = addresss_element.company.id
    if addresss_element.isActive:
        addresss_element.isActive = False
    else:
        addresss_element.isActive = True
    db.session.commit()
    # db.session.delete(addresss_element)
    # db.session.commit()
    return redirect(url_for('addCompany', item_id=item_id, proj_id=proj_id))


# TODO Project Module

@app.route('/add-project/proj-<proj_id>/item-<item_id>', methods=['GET', 'POST'])
def addProject(proj_id, item_id):
    with app.app_context():
        metadata_ = metadata()
        if request.method == "POST":
            len_project = len(projectMaster.query.all())

            data = request.form.to_dict(flat=False)
            quote_no = f"Q{date_today[2:4]}0000{len_project}"
            a = jsonify(data).json

            new_project = projectMaster(
                projectId=quote_no,
                projectRef=a['projectRef'][0],
                enquiryRef=a['enquiryRef'][0],
                enquiryReceivedDate=datetime.datetime.strptime(a['enquiryReceivedDate'][0], '%Y-%m-%d'),
                receiptDate=datetime.datetime.strptime(a['receiptDate'][0], '%Y-%m-%d'),
                bidDueDate=datetime.datetime.strptime(a['bidDueDate'][0], '%Y-%m-%d'),
                purpose=a['purpose'][0],
                custPoNo=a['custPoNo'][0],
                workOderNo=a['workOderNo'][0],
                status=a['status'][0],
                user=current_user,
                industry=getDBElementWithId(industryMaster, a['industry'][0]),
                region=getDBElementWithId(regionMaster, a['region'][0]),
            )
            db.session.add(new_project)
            db.session.commit()

            # add dummy Item 
            add_item = newProjectItem(new_project)

            project_element = db.session.query(projectMaster).filter_by(projectId=quote_no).first()

            addProjectRels(a['cname'][0], a['cnameE'][0], a['address'][0], a['addressE'][0], a['aEng'][0], a['cEng'][0],
                           project_element, 'create')

            flash('Project Added Successfully')
            print(a)
            return redirect(url_for('home', proj_id=add_item.project.id, item_id=add_item.id))

        # return render_template('projectdetails.html', dropdown=json.dumps(metadata_['notes_dict']), industries=metadata_['industries'], regions=metadata_['regions'], engineers=metadata_['engineers'], user=current_user, status=project_status_list, date=date_today, item=getDBElementWithId(itemMaster, item_id))
        return render_template('projectdetails.html', metadata=metadata_, user=current_user,
                               item=getDBElementWithId(itemMaster, item_id), page='addProject')


@app.route('/edit-project/proj-<proj_id>/item-<item_id>', methods=['GET', 'POST'])
def editProject(proj_id, item_id):
    metadata_ = metadata()
    notes_dict = metadata_['notes_dict_']
    project_element = projectMaster.query.get(int(proj_id))
    address_c, address_e, eng_a, eng_c = getEngAddrProject(project_element)
    if address_c != None:
        output_notes_dict = notes_dict_reorder(notes_dict, address_c.address.company.name, address_c.address.address)
        output_notes_dict_e = notes_dict_reorder(notes_dict, address_e.address.company.name, address_e.address.address)
        eng_a_id = eng_a.engineer.id
        eng_c_id = eng_c.engineer.id
    else:
        output_notes_dict = notes_dict
        output_notes_dict_e = notes_dict
        eng_a_id = None
        eng_c_id = None
    if request.method == "POST":
        data = request.form.to_dict(flat=False)
        a = jsonify(data).json
        a_eng = a.pop('aEng')
        c_eng = a.pop('cEng')
        c_name_c = a.pop('cname')
        c_name_e = a.pop('cnameE')
        address_c_ = a.pop('address')
        address_e_ = a.pop('addressE')
        industry = a.pop('industry')
        region = a.pop('region')
        # Convert date to datetime
        a['bidDueDate'][0] = datetime.datetime.strptime(a['bidDueDate'][0], '%Y-%m-%d')
        a['enquiryReceivedDate'][0] = datetime.datetime.strptime(a['enquiryReceivedDate'][0], '%Y-%m-%d')
        a['receiptDate'][0] = datetime.datetime.strptime(a['receiptDate'][0], '%Y-%m-%d')
        a['industry'] = [getDBElementWithId(industryMaster, industry[0])]
        a['region'] = [getDBElementWithId(regionMaster, region[0])]
        update_dict = a
        project_element.update(update_dict, project_element.id)
        industr_ = getDBElementWithId(industryMaster, industry[0])
        region_ = getDBElementWithId(regionMaster, region[0])
        # project_element.industry = industr_
        # project_element.region = region_
        # db.session.commit()
        addProjectRels(c_name_c[0], c_name_e[0], address_c_[0], address_e_[0], a_eng[0], c_eng[0], project_element,
                       'update')
        return redirect(url_for('editProject', proj_id=proj_id, item_id=item_id))
    return render_template('editproject.html', dropdown=json.dumps(output_notes_dict),
                           dropdown2=json.dumps(output_notes_dict_e), metadata=metadata_, user=current_user,
                           item=getDBElementWithId(itemMaster, item_id), project=project_element, eng_a=eng_a_id,
                           eng_c=eng_c_id, page='editProject')


# Valve Details Module
@app.route('/checkCaseExists', methods=['GET', 'POST'])
def checkCaseExists():
    itemId = request.args.get('itemId')
    case_data = db.session.query(caseMaster).filter_by(item=getDBElementWithId(itemMaster, int(itemId))).first()
    print(f"caseData {case_data}")
    if not case_data:
        return "no"
    else:
        return "yes"

@app.route('/valve-data/proj-<proj_id>/item-<item_id>', methods=['GET', 'POST'])
def valveData(proj_id, item_id):
    metadata_ = metadata()
    valve_element = db.session.query(valveDetailsMaster).filter_by(
        item=getDBElementWithId(itemMaster, int(item_id))).first()
    if request.method == "POST":
        data = request.form.to_dict(flat=False)
        a = jsonify(data).json
        # Changing string to db element to input into update method into db table
        balanceSeal_ = a['balanceseal'][0]
        a['balanceSeal__'] = [getDBElementWithId(balanceSeal, balanceSeal_)]
        bonnetType__ = a['bonnetType__'][0]
        a['bonnetType__'] = [getDBElementWithId(bonnetType, bonnetType__)]
        bonnet__ = a['bonnet__'][0]
        a['bonnet__'] = [getDBElementWithId(bonnet, bonnet__)]
        design = a['design'][0]
        a['design'] = [getDBElementWithId(designStandard, design)]
        endConnection__ = a['endConnection__'][0]
        a['endConnection__'] = [getDBElementWithId(endConnection, endConnection__)]
        endFinish__ = a['endFinish__'][0]
        a['endFinish__'] = [getDBElementWithId(endFinish, endFinish__)]
        flowCharacter__ = a['flowCharacter__'][0]
        a['flowCharacter__'] = [getDBElementWithId(flowCharacter, flowCharacter__)]
        flowDirection__ = a['flowDirection__'][0]
        a['flowDirection__'] = [getDBElementWithId(flowDirection, flowDirection__)]
        gasket__ = a['gasket__'][0]
        a['gasket__'] = [getDBElementWithId(gasket, gasket__)]
        packing__ = a['packing__'][0]
        a['packing__'] = [getDBElementWithId(packing, packing__)]
        studNut__ = a['studNut__'][0]
        a['studNut__'] = [getDBElementWithId(studNut, studNut__)]
        cage__ = a['cage__'][0]
        a['cage__'] = [getDBElementWithId(cageClamp, cage__)]
        packingType__ = a['packingType__'][0]
        a['packingType__'] = [getDBElementWithId(packingType, packingType__)]
        rating = a['rating'][0]
        a['rating'] = [getDBElementWithId(ratingMaster, rating)]
        seatLeakageClass__ = a['seatLeakageClass__'][0]
        a['seatLeakageClass__'] = [getDBElementWithId(seatLeakageClass, seatLeakageClass__)]
        material = a['material'][0]
        a['material'] = [getDBElementWithId(materialMaster, material)]
        fluid_state = getDBElementWithId(fluidState, int(valve_element.fluidStateId))
        if fluid_state:
            a['state'] = [fluid_state]
        else:
            a['state'] = [db.session.query(fluidState).filter_by(name='Liquid').first()]

        # bonnetExtDimension
        try:
            if a['bonnetExtDimension'][0] == '':
                a['bonnetExtDimension'][0] = None
            else:
                a['bonnetExtDimension'][0] = float(a['bonnetExtDimension'][0])
        except:
            a['bonnetExtDimension'][0] = None

        # Data Type conversion
        try:
            a['maxPressure'][0] = float(a['maxPressure'][0])
            a['maxTemp'][0] = float(a['maxTemp'][0])
            a['minTemp'][0] = float(a['minTemp'][0])
            a['shutOffDelP'][0] = float(a['shutOffDelP'][0])
            a['quantity'][0] = int(a['quantity'][0])
        except Exception as e:
            flash(f'Error: {e}')
            pass

        # Adding Data based on Valve style
        style = a['valvestyle'][0]
        a['style'] = [getDBElementWithId(valveStyle, style)]
        try:
            if a['style'][0].name in ['Globe Straight', 'Globe Angle']:
                # stem [Shaft], plug [Disc], seat [Seat], trimTypeG [trimType__]
                shaft__ = a['shaft'][0]
                a['shaft__'] = [getDBElementWithId(shaft, shaft__)]
                disc__ = a['plug'][0]
                a['disc__'] = [getDBElementWithId(disc, disc__)]
                seat__ = a['seat'][0]
                a['seat__'] = [getDBElementWithId(seat, seat__)]
                trimType__ = a['trimtypeG'][0]
                a['trimType__'] = [getDBElementWithId(trimType, trimType__)]

                print(shaft__)
            elif a['style'][0].name in ['Butterfly Lugged Wafer', 'Butterfly Double Flanged']:
                # shaft [Shaft], disc [Disc], seal [Seat], trimTypeB [trimType__]
                shaft__ = a['stem'][0]
                a['shaft__'] = [getDBElementWithId(shaft, shaft__)]
                disc__ = a['disc'][0]
                a['disc__'] = [getDBElementWithId(disc, disc__)]
                seat__ = a['seal'][0]
                a['seat__'] = [getDBElementWithId(seat, seat__)]
                trimType__ = a['trimtypeB'][0]
                a['trimType__'] = [getDBElementWithId(trimType, trimType__)]
                print(shaft__)
            else:
                pass
        except:
            a['shaft__'] = [None]
            a['disc__'] = [None]
            a['seat__'] = [None]
            a['trimType__'] = [None]

        # remove unwanted keys from a dict
        a.pop('valvestyle')
        try:
            a.pop('shaft')
            a.pop('plug')
            a.pop('seat')
            a.pop('trimtypeG')
            a.pop('stem')
            a.pop('disc')
            a.pop('seal')
            a.pop('trimtypeB')
        except:
            pass
        a.pop('balanceseal')
        # a.pop('shaft')
        # print(a['shaft__'][0].name)
        update_dict = a
        valve_element.update(update_dict, valve_element.id)

        # Logic for pressure Temp rating
        # minTemp_ = float(a['minTemp'][0])
        # maxTemp_ = float(a['maxTemp'][0])
        # try:
        #     presTempRatingElement = db.session.query(pressureTempRating).filter_by(material=a['material'][0], rating=a['rating'][0]).first()
        #     if maxTemp_ > float(presTempRatingElement.maxTemp):
        #         error_message = f"Temp {maxTemp_} is higher than {presTempRatingElement.maxTemp}"
        #     else:
        #         error_message = ""
        # except:
        #     error_message = ""
        # print(f"Temp {maxTemp_} is higher than {presTempRatingElement.maxTemp}")
        flash('Data Updated Successfully')
        return render_template('valvedata.html', item=getDBElementWithId(itemMaster, int(item_id)), user=current_user,
                           metadata=metadata_, valve=valve_element, page='valveData', msg='')
    return render_template('valvedata.html', item=getDBElementWithId(itemMaster, int(item_id)), user=current_user,
                           metadata=metadata_, valve=valve_element, page='valveData', msg='')


@app.route('/handle_change')
def handle_change():
    print('workkkkksssss')
    maxTemp_b = request.args.get('maxTemp')
    minTemp_b = request.args.get('minTemp')
    maxPres = request.args.get('maxPressure')
    materialId = request.args.get('materialValue')
    ratingId = request.args.get('ratingValue')
    maxPresUnit = request.args.get('maxPresUnit')
    maxTempUnit = request.args.get('maxTempUnit')
    minTempUnit = request.args.get('minTempUnit')
    prev_units = maxPresUnit.split(' ')
    

    maxPressure = meta_convert_P_T_FR_L('P', float(maxPres), maxPresUnit,
                                        'bar (a)', 1.0 * 1000)

    
    

    maxTemp = meta_convert_P_T_FR_L('T', float(maxTemp_b), maxTempUnit,
                                        'C',1000)
    minTemp = meta_convert_P_T_FR_L('T', float(minTemp_b), minTempUnit,
                                        'C',1000)
    
    material = getDBElementWithId(materialMaster, materialId)
    rating = getDBElementWithId(ratingMaster, ratingId)
    
    # print(f'MinTemperaturesspp , {material[0]}, {rating[0]}')
    presTempRatingElement = db.session.query(pressureTempRating).filter_by(material=material, rating=rating).all()
    print(f'PresTemprating {presTempRatingElement}')
    # print(f'presTempRatingElement {presTempRatingElement}')
    tempcnt = 0
    for element in presTempRatingElement:
        print(f'element {element}')
        a_maxTemp = element.maxTemp
        a_minTemp = element.minTemp
        a_pressure = element.pressure

        if (float(maxTemp) <= float(a_maxTemp) and float(maxTemp) > float(a_minTemp) ) and ( float(minTemp) >= float(a_minTemp) and float(minTemp) < float(a_maxTemp)) and (maxTemp >= minTemp):
            tempcnt+=1
            if float(maxPressure) <= float(a_pressure):
                print(f'inside pressComparision lESS')
                pass 
                return ""
            else:
                print(f'inside Tempcomparision Max')
                return f'Pressure {maxPressure} bar exceeds {a_pressure} bar'
    print(f'tempcnt {tempcnt}')
    if tempcnt == 0:
        print(f'kskskkskskk {maxTemp},{minTemp}')
        if (float(maxTemp) < float(minTemp)):
            return f"Minimum Temperature should not be greater than maximum temperature"
        elif float(maxTemp) > float(element.maxTemp):
            return f'Max Temperature {maxTemp} C exceeds {a_maxTemp} C'
        elif float(maxTemp) < float(element.minTemp):
            return f'Max Temperature {maxTemp} C is much lower than {element.minTemp} C'
        elif float(minTemp) < float(element.minTemp):
            return f'Min Temperature {minTemp} C exceeds {a_minTemp} C'
        elif float(minTemp) > float(element.maxTemp):
            return f'Min Temperature {minTemp} C is much higher than {element.maxTemp} C'
    return f""
# Valve Sizing Module

def power_level_liquid(inletPressure, outletPressure, sGravity, Cv):
    a_ = ((inletPressure - outletPressure) ** 1.5) * Cv
    b_ = sGravity * 2300
    c_ = a_ / b_
    return round(c_, 3)


# TODO - Trim exit velocities and other velocities
def getMultipliers(trimType, numberOfTurns):
    trimDict = {"microspline": 0.7, "Trickle": 0.92, "Contoured": 3.4167, "Cage": 3.2, "MLT": 0.53, "other": 0.7, "1cc": 3, "2cc": 1.8641, "3cc": 1.2548, "4cc": 0.9615, "do": 2.5, "to": 2.5}
    turnsDict = {2: 0.88, 4: 0.9, 6: 0.91, 8: 0.92, 10: 0.93, 12: 0.96, "other": 1}
    try:
        K1 = trimDict[trimType]
        K2 = turnsDict[numberOfTurns]
    except:
        K1 = 1
        K2 = 1

    return K1, K2


def trimExitVelocity(inletPressure, outletPressure, density, trimType, numberOfTurns):
    a_ = math.sqrt(((inletPressure - outletPressure)) / density)
    K1, K2 = getMultipliers(trimType, numberOfTurns)
    print(f"tex values: {inletPressure}, {outletPressure}, {K1}, {density}, {a_}")
    return a_ * K1

def trimExitVelocityLiquid(inletPressure, outletPressure, trimType, specificGravity):
    trim_dict = {
        'Contour': 3.416712,
        'Ported': 3.2,
        "Anti-Cavitation I": 1.864196,
        "Anti-Cavitation II": 1.254847,
        "Anti-Cavitation III": 0.961509,
        "Double Offset": 2.5,
        "Triple Offset": 2.5,
        "Microspline": 3.416712,
        "MHC": 3
        }
    try:
        K_value = trim_dict[trimType] 
    except:
        K_value = trim_dict['Contour']

    output = K_value * math.sqrt((inletPressure-outletPressure)/specificGravity)
    return output


# TODO - New Trim Exit velocity formulae
def inletDensity(iPres, MW, R, iTemp):
    a_ = iPres * MW / (R * iTemp)
    return round(a_, 2)

def outletDensity(iPres, oPres, MW, R, iTemp):
    Pi = inletDensity(iPres, MW, R, iTemp)
    a = Pi * (oPres / iPres)
    return round(a, 2)

def tex_new(calculatedCV, ratedCV, port_area, flowrate, iPres, oPres, MW, R, iTemp, fluid_state):
    # density in kg/m3, fl in m3/hr, area in m2
    port_area = port_area * 0.000645
    tex_area = (calculatedCV / ratedCV) * port_area
    tex_vel = flowrate / tex_area
    oDensity = outletDensity(iPres, oPres, MW, R, iTemp)
    ke = (oDensity * tex_vel ** 2) / 19.62
    print(
        f"tex_new inputs: {calculatedCV}, {ratedCV}, {port_area}, {flowrate}, {iPres}, {oPres}, {MW}, {R}, {iTemp}, {fluid_state}, {tex_vel}, {oDensity}, {tex_area}")
    if fluid_state == 'Liquid':
        return round(tex_vel, 3)
    else:
        return round(ke * 0.001422, 3)


def getKc(valveSize, trimType_, pressure, valveStyle, fl):
    with app.app_context():
        kc_filter = kcTable.query.filter(kcTable.valveStyle==valveStyle).filter(kcTable.trimType==trimType_).filter(kcTable.minSize <= valveSize).filter(kcTable.maxSize >= valveSize).filter(kcTable.minDelP <= pressure).filter(kcTable.maxDelP >= pressure).all()
        if len(kc_filter) > 0:
            kc_element = kc_filter[0]
            formula_number = kc_element.formula
            formula_dict = {1: 0.99, 2: 1, 3: 0.5 * fl * fl, 4: 0.85 * fl * fl, 5: fl * fl}
            output_value = formula_dict[formula_number]
            return output_value
        else:
            return None


# print(getKc(2, 'Contour', 50, 'Globe Straight', 0.9))
# getting kc value
def getKCValue(size__, t_type, pressure, v_type, fl):
    with app.app_context():
        kc_dict_1 = [{'v_tye': 'globe', 'size': (1, 4), 'material': '316 SST', 'trim': 'contour', 'pressure': (0, 75),
                      'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (1, 4), 'material': '316 SST', 'trim': 'contour', 'pressure': (75, 100),
                      'kc_formula': '5'}, {'v_tye': 'globe', 'size': (1, 4), 'material': '316 SST', 'trim': 'contour',
                                           'pressure': (100, 9000), 'kc_formula': '4'},
                     {'v_tye': 'globe', 'size': (1, 4), 'material': '416 SST', 'trim': 'contour', 'pressure': (0, 75),
                      'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (1, 4), 'material': '416 SST', 'trim': 'contour', 'pressure': (75, 100),
                      'kc_formula': '5'}, {'v_tye': 'globe', 'size': (1, 4), 'material': '416 SST', 'trim': 'contour',
                                           'pressure': (100, 9000), 'kc_formula': '4'},
                     {'v_tye': 'globe', 'size': (1, 4), 'material': '440C', 'trim': 'contour', 'pressure': (0, 75),
                      'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (1, 4), 'material': '440C', 'trim': 'contour', 'pressure': (75, 100),
                      'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (1, 4), 'material': '440C', 'trim': 'contour', 'pressure': (100, 9000),
                      'kc_formula': '4'},
                     {'v_tye': 'globe', 'size': (1, 4), 'material': '316 / Alloy', 'trim': 'contour',
                      'pressure': (0, 75), 'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (1, 4), 'material': '316 / Alloy', 'trim': 'contour',
                      'pressure': (75, 100), 'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (1, 4), 'material': '316 / Alloy', 'trim': 'contour',
                      'pressure': (100, 9000), 'kc_formula': '4'},
                     {'v_tye': 'globe', 'size': (1, 2), 'material': '416 SST', 'trim': 'ported', 'pressure': (0, 300),
                      'kc_formula': '2'}, {'v_tye': 'globe', 'size': (1, 2), 'material': '416 SST', 'trim': 'ported',
                                           'pressure': (300, 9000), 'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (1, 2), 'material': '440C', 'trim': 'ported', 'pressure': (0, 300),
                      'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (1, 2), 'material': '440C', 'trim': 'ported', 'pressure': (300, 9000),
                      'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (1, 2), 'material': '440C', 'trim': 'ported', 'pressure': (0, 200),
                      'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (1, 2), 'material': '316 / Alloy 6', 'trim': 'ported',
                      'pressure': (0, 300), 'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (1, 2), 'material': '317 / Alloy 6', 'trim': 'ported',
                      'pressure': (300, 9000), 'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (1, 2), 'material': '318 / Alloy 6', 'trim': 'ported',
                      'pressure': (0, 200), 'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (1, 2), 'material': '319 / Alloy 6', 'trim': 'ported',
                      'pressure': (200, 9000), 'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (1, 12), 'material': '316 SST', 'trim': 'ported', 'pressure': (0, 100),
                      'kc_formula': '2'}, {'v_tye': 'globe', 'size': (1, 12), 'material': '316 SST', 'trim': 'ported',
                                           'pressure': (100, 9000), 'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (3, 4), 'material': '416 SST', 'trim': 'ported', 'pressure': (0, 200),
                      'kc_formula': '2'}, {'v_tye': 'globe', 'size': (3, 4), 'material': '416 SST', 'trim': 'ported',
                                           'pressure': (200, 9000), 'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (3, 4), 'material': '440C', 'trim': 'ported', 'pressure': (200, 9000),
                      'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (6, 12), 'material': '416 SST', 'trim': 'ported', 'pressure': (0, 100),
                      'kc_formula': '2'}, {'v_tye': 'globe', 'size': (6, 12), 'material': '416 SST', 'trim': 'ported',
                                           'pressure': (100, 9000), 'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (6, 12), 'material': '440C', 'trim': 'ported', 'pressure': (0, 100),
                      'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (6, 12), 'material': '440C', 'trim': 'ported', 'pressure': (100, 9000),
                      'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (6, 12), 'material': '320 / Alloy 6', 'trim': 'ported',
                      'pressure': (0, 100), 'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (6, 12), 'material': '321 / Alloy 6', 'trim': 'ported',
                      'pressure': (100, 9000), 'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (16, 24), 'material': '416 SST', 'trim': 'ported', 'pressure': (0, 50),
                      'kc_formula': '2'}, {'v_tye': 'globe', 'size': (16, 24), 'material': '416 SST', 'trim': 'ported',
                                           'pressure': (50, 9000), 'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (16, 24), 'material': '440C', 'trim': 'ported', 'pressure': (0, 50),
                      'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (16, 24), 'material': '440C', 'trim': 'ported', 'pressure': (50, 9000),
                      'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (16, 24), 'material': '322 / Alloy 6', 'trim': 'ported',
                      'pressure': (0, 50), 'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (16, 24), 'material': '323 / Alloy 6', 'trim': 'ported',
                      'pressure': (50, 9000), 'kc_formula': '5'},
                     {'v_tye': 'butterfly', 'size': (2, 4), 'material': '-', 'trim': 'do', 'pressure': (0, 50),
                      'kc_formula': '2'},
                     {'v_tye': 'butterfly', 'size': (2, 4), 'material': '-', 'trim': 'do', 'pressure': (50, 9000),
                      'kc_formula': '3'},
                     {'v_tye': 'butterfly', 'size': (6, 36), 'material': '-', 'trim': 'do', 'pressure': (0, 9000),
                      'kc_formula': '3'},
                     {'v_tye': 'globe', 'size': (1, 2), 'material': '', 'trim': 'cavitrol_3_1', 'pressure': (0, 600),
                      'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (1, 2), 'material': '', 'trim': 'cavitrol_3_1', 'pressure': (600, 9000),
                      'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (1, 2), 'material': '', 'trim': 'cavitrol_3_1', 'pressure': (0, 500),
                      'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (1, 2), 'material': '', 'trim': 'cavitrol_3_1', 'pressure': (500, 1440),
                      'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (1, 2), 'material': '', 'trim': 'cavitrol_3_1', 'pressure': (0, 400),
                      'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (1, 2), 'material': '', 'trim': 'cavitrol_3_1', 'pressure': (400, 1440),
                      'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (1, 2), 'material': '', 'trim': 'cavitrol_3_2', 'pressure': (0, 2160),
                      'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (3, 6), 'material': '', 'trim': 'cavitrol_3_2', 'pressure': (0, 1800),
                      'kc_formula': '2'}, {'v_tye': 'globe', 'size': (3, 6), 'material': '', 'trim': 'cavitrol_3_2',
                                           'pressure': (1800, 9000), 'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (8, 24), 'material': '', 'trim': 'cavitrol_3_2', 'pressure': (0, 1200),
                      'kc_formula': '2'}, {'v_tye': 'globe', 'size': (8, 24), 'material': '', 'trim': 'cavitrol_3_2',
                                           'pressure': (1200, 9000), 'kc_formula': '5'},
                     {'v_tye': 'globe', 'size': (1, 24), 'material': '', 'trim': 'cavitrol_3_3', 'pressure': (0, 3000),
                      'kc_formula': '2'},
                     {'v_tye': 'globe', 'size': (1, 12), 'material': '', 'trim': 'cavitrol_3_4', 'pressure': (0, 3000),
                      'kc_formula': '2'}, {'v_tye': 'globe', 'size': (1, 12), 'material': '', 'trim': 'cavitrol_3_4',
                                           'pressure': (3000, 4000), 'kc_formula': '1'}]

        # kc = db.session.query(kcTable).filter(kcTable.min_size <= int(size__), kcTable.max_size >= int(size__),
        #                                       kcTable.trim_type == t_type,
        #                                       kcTable.min_pres <= float(pressure), kcTable.max_pres >= float(pressure),
        #                                       kcTable.valve_style == v_type).first()

        output_list_kc = []
        for kc in kc_dict_1:
            if kc['v_tye'] == v_type and (kc['size'][0] <= size__ <= kc['size'][1]) and (
                    kc['pressure'][0] <= pressure <= kc['pressure'][1]) and kc['trim'] == t_type:
                output_list_kc.append(kc)

        formula_dict = {1: 0.99, 2: 1, 3: 0.5 * fl * fl, 4: 0.85 * fl * fl, 5: fl * fl}
        print(f"output kc list: {output_list_kc}")
        print(v_type, size__, pressure, t_type)

        # print(formula_dict[int(kc.kc_formula)])
        if len(output_list_kc) >= 1:
            a__ = formula_dict[int(output_list_kc[0]['kc_formula'])]
            print(f"kc forumual: {a__}")
        else:
            print("Didn't get KC value")
            a__ = 1

        return round(a__, 3)

@app.route('/unit_change_stemDia')
def unit_change_stemDia():
    prev_unit = request.args.get('prev_unit')
    final_unit = request.args.get('final_unit')
    param_values = json.loads(request.args.get('param_values'))
    print(f'STEMDIAUNITS {prev_unit},{final_unit},{param_values}')
    param_values = [int(value) for value in param_values]
    desc_final_value = []
    if final_unit == 'mm':
        stem_elements = db.session.query(stemSize).filter(stemSize.id.in_(param_values)).all()
        stem_values = [float(Fraction(stem.stemDia)) for stem in stem_elements]
        print(f'stem_values {stem_values}')
        for stem in stem_values:
            final_value = meta_convert_P_T_FR_L('L', stem, prev_unit,
                                        final_unit,
                                        1000)
            desc_final_value.append(round(final_value,3))
    elif final_unit == 'inch':
        stem_elements = db.session.query(stemSize).filter(stemSize.id.in_(param_values)).all()
        for stem in stem_elements:
            desc_final_value.append(stem.stemDia)


            



    print(f'stem_elements {desc_final_value}') 

    # desc_final_value = [prev_unit,final_unit,param_values]
    return json.dumps(desc_final_value)



@app.route('/unit_change')
def unit_change():

    prev_unit = request.args.get('prev_unit')
    final_unit = request.args.get('final_unit')
    params = request.args.get('params')
    param_values = json.loads(request.args.get('param_values'))
    specific_gravity = request.args.get('specific_gravity')
    fluid_type = request.args.get('fluid_type')
    
    
    # if params == 'stemDia':
    #     param_values = [float(Fraction(''.join(str(value)))) if value else None for value in param_values]
    # else:
    param_values = [float(value) if value else None for value in param_values]
    print(f'unitchange_param_values{param_values}')


    if specific_gravity is not None:
        specific_gravity = json.loads(specific_gravity)
        specific_gravity = [float(value) if value else 1.0 for value in specific_gravity]
    else:
        specific_gravity = [1.0]

   
    print(f'jshshhh {prev_unit},{final_unit},{param_values},{specific_gravity},{params}')
    desc_final_value = []
    volume_params = ['clearanceVolUnit','sweptVolUnit']
    area_params = ['Ua','stemArea','diaphragm_ea','diaphragmArea']
    length_params = ['actTravel','inletlength','outletlength','valvelength','valveSize','seatDia','stemDia','plugDia','valveTravel','negGrad','actTravel','springWindup','valveSize','discDia','shaftDia','packingRadial']
    force_params = ['spring_rateUnit','packFricton','valveThrustClose','valveThrustOpen','shutOffForce','maxSpringLoad','actThrustClose','actThrustOpen','reqHandWheel']
    pressure_params = ['setPressureUnit','lower_benchsetUnit','upper_benchsetUnit','inpres','outpres','vaporPres','critPres','shutoffPres','maxPres','ipres','opres','delpflow','lowBenchSet','UpBenchSet','maxAirSupply','setPressure','frictionBand','setPUnit','maxAirUnit','delp']
    torque_params = ['stUnit','ptUnit','ftUnit','btoUnit','rtoUnit','etoUnit','btcUnit','rtcUnit','etcUnit','mastUnit','stStartUnit','stMidUnit','stEndUnit','atStartUnit','atMidUnit','atEndUnit','handWheelUnit']
    print(f'params_GET {params}')
    if params == 'flowrate':
        for i in range(len(param_values)):
            if param_values[i]:
                print(f'ssjsj {param_values[i]}')
                if fluid_type == 'gas':
                    final_value = meta_convert_P_T_FR_L('FR', param_values[i], prev_unit,
                                    final_unit,0.1*1000) 
                else:
                    final_value = meta_convert_P_T_FR_L('FR', param_values[i], prev_unit,
                                                        final_unit,
                                                        specific_gravity[i] * 1000) 

                desc_final_value.append(round(final_value,2))
            else:
                desc_final_value.append(None) 
        print(f'FLOWRATE {desc_final_value}')

    elif params in pressure_params:
        print(f'KKSJJSJSJSJVAPO')
        for i in range(len(param_values)):
            if param_values[i]:
                if params != "shutoffPres" and params!='delpflow':
                    print(f'IM VAPOR {str(prev_unit)+ "(a)"}')
                    final_value = meta_convert_P_T_FR_L('P', param_values[i], prev_unit,
                                                  final_unit, specific_gravity[i] * 1000)
                else:
                    print('INSIDE DELP')
                    final_value = meta_convert_P_T_FR_L('P', param_values[i], str(prev_unit)+ "(a)",
                                                  str(final_unit)+ "(a)", specific_gravity[i] * 1000)
                print(f'shhshsh {final_value}')
                if params != "shutoffPres" and params!='delpflow':
                    
                    desc_final_value.append(round(final_value,2))
               
            else:
                desc_final_value.append(None) 
    elif params == "temperature" or params == "maxTemp" or params == "minTemp":
        print('Temp Called')
        for i in range(len(param_values)):
            print(f'before {param_values[i]}')
            if param_values[i] != None:
                print(f'ssjsj {param_values[i]},{prev_unit},{final_unit}')
                final_value = meta_convert_P_T_FR_L('T', param_values[i], prev_unit,
                                                        final_unit,
                                                        1000)

                desc_final_value.append(round(final_value,2))
            else:
                desc_final_value.append(None) 

    elif params in length_params:
        print('IIII CALLED')
        for i in range(len(param_values)):
            
            if param_values[i] != None:
                print(f'ssjsj {param_values[i]},{prev_unit},{final_unit}')
                final_value = meta_convert_P_T_FR_L('L', param_values[i], prev_unit,
                                                        final_unit,
                                                        1000)
                

                desc_final_value.append(round(final_value,2))
            else:
                desc_final_value.append(None) 
            
        
        print(f'desc_final_value {desc_final_value}')
    elif params in area_params:
        for i in range(len(param_values)):
            if param_values[i] != None:
                print(f'ssjsj {param_values[i]},{prev_unit},{final_unit}')
                final_value = meta_convert_P_T_FR_L('A', param_values[i], prev_unit,
                                                        final_unit,
                                                        1000)

                desc_final_value.append(round(final_value,2))
            else:
                desc_final_value.append(None)   
    elif params in force_params:
        for i in range(len(param_values)):
            if param_values[i] != None:
                print(f'ssjsj {param_values[i]},{prev_unit},{final_unit}')
                final_value = meta_convert_P_T_FR_L('F', param_values[i], prev_unit,
                                                        final_unit,
                                                        1000)

                desc_final_value.append(round(final_value,2))
            else:
                desc_final_value.append(None)   
    elif params in volume_params:
        for i in range(len(param_values)):
            if param_values[i] != None:
                print(f'ssjsjFFF {param_values[i]},{prev_unit},{final_unit}')
                final_value = meta_convert_P_T_FR_L('V', param_values[i], prev_unit,
                                                        final_unit,
                                                        1000)
                print(f'VOLUME {final_value}')

                desc_final_value.append(round(final_value,5))
            else:
                desc_final_value.append(None)   
    elif params in torque_params:
        for i in range(len(param_values)):
            if param_values[i] != None:
                print(f'ssjsjFFF {param_values[i]},{prev_unit},{final_unit}')
                final_value = meta_convert_P_T_FR_L('TOR', param_values[i], prev_unit,
                                                        final_unit,
                                                        1000)
                print(f'TOR {final_value}')

                desc_final_value.append(round(final_value,2))
            else:
                desc_final_value.append(None)   




    print(f'desc_final_value {desc_final_value}')


    return json.dumps(desc_final_value)

def getOutputs(flowrate_form, fl_unit_form, inletPressure_form, iPresUnit_form, outletPressure_form, oPresUnit_form,
               inletTemp_form,
               iTempUnit_form, vaporPressure_form, vPresUnit_form, specificGravity, viscosity, xt_fl, criticalPressure_form,
               cPresUnit_form,
               inletPipeDia_form, iPipeUnit_form, iSch, outletPipeDia_form, oPipeUnit_form, oSch, densityPipe, sosPipe,
               valveSize_form, vSizeUnit_form,
               seatDia, seatDiaUnit, ratedCV, rw_noise, item_selected, fluidName, valve_element, i_pipearea_element, port_area_, valvearea_element):
    # change into float/ num
    flowrate_form, fl_unit_form, inletPressure_form, iPresUnit_form, outletPressure_form, oPresUnit_form, inletTemp_form, iTempUnit_form, vaporPressure_form, vPresUnit_form, specificGravity, viscosity, xt_fl, criticalPressure_form, cPresUnit_form, inletPipeDia_form, iPipeUnit_form, iSch, outletPipeDia_form, oPipeUnit_form, oSch, densityPipe, sosPipe, valveSize_form, vSizeUnit_form, seatDia, seatDiaUnit, ratedCV, rw_noise, item_selected = float(
        flowrate_form), fl_unit_form, float(inletPressure_form), iPresUnit_form, float(
        outletPressure_form), oPresUnit_form, float(inletTemp_form), iTempUnit_form, float(
        vaporPressure_form), vPresUnit_form, float(specificGravity), float(viscosity), float(xt_fl), float(
        criticalPressure_form), cPresUnit_form, float(inletPipeDia_form), iPipeUnit_form, iSch, float(
        outletPipeDia_form), oPipeUnit_form, oSch, float(densityPipe), float(sosPipe), float(
        valveSize_form), vSizeUnit_form, float(seatDia), seatDiaUnit, float(ratedCV), float(rw_noise), item_selected

    # check whether flowrate, pres and l are in correct units
    # 1. flowrate
    # print(f' UNITSFORVALVEDATA {flowrate_form},{fl_unit_form},{inletPressure_form},{iPresUnit_form},{outletPressure_form},{oPresUnit_form},{inletTemp_form},{iTempUnit_form},{vaporPressure},{vPresUnit_form},{criticalPressure_form},{cPresUnit_form},{inletPipeDia_form},{iPipeUnit_form},{outletPipeDia_form},{oPipeUnit_form},{valveSize_form},{vSizeUnit_form}')
    inletPipeDia_v = round(meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                                 1000))
    print(f'unitlength {iPipeUnit_form},{oPipeUnit_form},{vSizeUnit_form}')
    i_pipearea_element = i_pipearea_element
    try:
        thickness_pipe = float(i_pipearea_element.thickness)
    except:
        thickness_pipe = 1.24
    print(f"thickness: {thickness_pipe}")
    # if fl_unit_form not in ['m3/hr', 'gpm']:
    print(f'Before FL {flowrate_form},{fl_unit_form},{specificGravity}')
    if fl_unit_form:
        flowrate_liq = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form,
                                             'm3/hr',
                                             specificGravity * 1000)
        fr_unit = 'm3/hr'
    else:
        fr_unit = fl_unit_form
        flowrate_liq = flowrate_form
    print(f'AFTER FL {flowrate_liq},{fr_unit}')

    # 2. Pressure
    # A. inletPressure  
    # iPresUnit_form = iPresUnit_form.split(' ')
    # print(f'InletPressureB4 {iPresUnit_form[0]},{iPresUnit_form[1]},{inletPressure_form}')
    
    # if iPresUnit_form[1] == '(g)':
        # inletPressure_form_new = meta_convert_g_to_a(inletPressure_form,iPresUnit_form[0])
        # print(f'Intermediates {inletPressure_form_new}')
    # else:
        # inletPressure_form_new = inletPressure_form
    # if iPresUnit_form[0] not in ['kPa', 'bar', 'psia']:
    # if iPresUnit_form[0]:
    inletPressure_liq = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form,
                                                  'bar (a)', specificGravity * 1000)
    iPres_unit = 'bar (a)'

    print(f'InPressureafter {iPres_unit},{inletPressure_liq}')

    # B. outletPressure
    # oPresUnit_form = oPresUnit_form.split(' ')
    # if oPresUnit_form[0] not in ['kPa', 'bar', 'psia']:
    # if oPresUnit_form[1] == '(g)':
    #     outletPressure_form_new = meta_convert_g_to_a(outletPressure_form,oPresUnit_form[0])
    #     print(f'Intermediates {outletPressure_form_new}')
    # else:
    #     outletPressure_form_new = outletPressure_form

    # if oPresUnit_form:
    outletPressure_liq = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                                   'bar (a)', specificGravity * 1000)
    oPres_unit = 'bar (a)'
    # else:
    #     oPres_unit = oPresUnit_form[0]
    #     outletPressure_liq = outletPressure_form

    # C. vaporPressure
    # vPresUnit_form = vPresUnit_form.split(' ')

    # if vPresUnit_form[1] == '(g)':
    #     vaporPressure_form_new = meta_convert_g_to_a(vaporPressure,vPresUnit_form[0])
    #     print(f'Intermediates {vaporPressure_form_new}')
    # else:
    #     vaporPressure_form_new = vaporPressure
    # if vPresUnit_form[0] not in ['kPa', 'bar', 'psia']:
    # if vPresUnit_form:
    print(f'VAPORPRESSSSSSSSSSSSSS BF {vaporPressure_form},{vPresUnit_form}')
    vaporPressure = meta_convert_P_T_FR_L('P', vaporPressure_form, vPresUnit_form, 'bar (a)',
                                              specificGravity * 1000)
    vPres_unit = 'bar (a)'
    print(f'VAPORPRESSSSSSSSSSSSSS AF {vaporPressure},{vPres_unit}')
    # else:
    #     vPres_unit = vPresUnit_form[0]

    # D. Critical Pressure
    # cPresUnit_form = cPresUnit_form.split(' ')
    # if cPresUnit_form[1] == '(g)':
    #     criticalPressure_form_new = meta_convert_g_to_a(criticalPressure_form,cPresUnit_form[0])
    #     print(f'Intermediates {criticalPressure_form_new}')
    # else:
    #     criticalPressure_form_new = criticalPressure_form
    # if cPresUnit_form[0] not in ['kPa', 'bar', 'psia']:
    # if cPresUnit_form[0]:
    criticalPressure_liq = meta_convert_P_T_FR_L('P', criticalPressure_form,
                                                     cPresUnit_form, 'bar (a)',
                                                     specificGravity * 1000)
    cPres_unit = 'bar (a)'
    # else:
    #     cPres_unit = cPresUnit_form[0]
    #     criticalPressure_liq = criticalPressure_form
    print(f'HHNEWCRITICAL {criticalPressure_liq},{cPres_unit}')
    if fr_unit == 'm3/hr':
        length_unit_list_calculation = ['mm']
    elif fr_unit == 'gpm':
        length_unit_list_calculation = ['inch']
    else: 
        length_unit_list_calculation = ['mm']

    # 3. Length
        
    print(f'unitlength {iPipeUnit_form},{oPipeUnit_form},{vSizeUnit_form},{length_unit_list_calculation},{thickness_pipe}')
    print(f'LENGTHHHHHHHHHHHHHH B4 {inletPipeDia_form},{iPipeUnit_form}')
    if iPipeUnit_form not in length_unit_list_calculation:
        inletPipeDia_liq = meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form,
                                                 'mm',
                                                 specificGravity * 1000) - 2 * thickness_pipe
        iPipe_unit = 'mm'
    else:
        iPipe_unit = iPipeUnit_form
        inletPipeDia_liq = inletPipeDia_form - 2 * thickness_pipe 
    print(f'LENGTHHHHHHHHHHHHHH AF {inletPipeDia_liq},{iPipe_unit}')
    
    if oPipeUnit_form not in length_unit_list_calculation:
        outletPipeDia_liq = meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form,
                                                  'mm', specificGravity * 1000) - 2 * thickness_pipe
        oPipe_unit = 'mm'
    else:
        oPipe_unit = oPipeUnit_form
        outletPipeDia_liq = outletPipeDia_form - 2 * thickness_pipe

    if vSizeUnit_form not in length_unit_list_calculation:
        vSize_liq = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                          'mm', specificGravity * 1000)
        vSize_unit = 'mm'
    else:
        vSize_unit = vSizeUnit_form
        vSize_liq = valveSize_form
    
    v_size_for_initial_cv = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                          'mm', specificGravity * 1000)

    print(f"dia of pipeget: {outletPipeDia_liq}, {inletPipeDia_liq}")

    service_conditions_sf = {'flowrate': flowrate_liq, 'flowrate_unit': fr_unit,
                             'iPres': inletPressure_liq, 'oPres': outletPressure_liq,
                             'iPresUnit': iPres_unit,
                             'oPresUnit': oPres_unit, 'temp': inletTemp_form,
                             'temp_unit': iTempUnit_form, 'sGravity': specificGravity,
                             'iPipeDia': inletPipeDia_liq,
                             'oPipeDia': outletPipeDia_liq,
                             'valveDia': vSize_liq, 'iPipeDiaUnit': iPipe_unit,
                             'oPipeDiaUnit': oPipe_unit, 'valveDiaUnit': vSize_unit,
                             'C': 0.075 * v_size_for_initial_cv * v_size_for_initial_cv, 'FR': 1, 'vPres': vaporPressure, 'Fl': xt_fl,
                             'Ff': 0.90,
                             'cPres': criticalPressure_liq,
                             'FD': 1, 'viscosity': viscosity}
    

    service_conditions_1 = service_conditions_sf
    print(str(service_conditions_1['iPresUnit']).split(' ')[0])
    N1_val = N1[(service_conditions_1['flowrate_unit'], str(service_conditions_1['iPresUnit']).split(' ')[0])]
    N2_val = N2[service_conditions_1['valveDiaUnit']]
    N4_val = N4[(service_conditions_1['flowrate_unit'], service_conditions_1['valveDiaUnit'])]
    print('B4outputcv')
    result_1 = CV(service_conditions_1['flowrate'], service_conditions_1['C'],
                  service_conditions_1['valveDia'],
                  service_conditions_1['iPipeDia'],
                  service_conditions_1['oPipeDia'], N2_val, service_conditions_1['iPres'],
                  service_conditions_1['oPres'],
                  service_conditions_1['sGravity'], N1_val, service_conditions_1['FD'],
                  service_conditions_1['vPres'],
                  service_conditions_1['Fl'], service_conditions_1['cPres'], N4_val,
                  service_conditions_1['viscosity'], thickness_pipe)

    result = CV(service_conditions_1['flowrate'], result_1,
                service_conditions_1['valveDia'],
                service_conditions_1['iPipeDia'],
                service_conditions_1['oPipeDia'], N2_val, service_conditions_1['iPres'],
                service_conditions_1['oPres'],
                service_conditions_1['sGravity'], N1_val, service_conditions_1['FD'],
                service_conditions_1['vPres'],
                service_conditions_1['Fl'], service_conditions_1['cPres'], N4_val,
                service_conditions_1['viscosity'], thickness_pipe)
    ff_liq = FF(service_conditions_1['vPres'], service_conditions_1['cPres'])
    chokedP = delPMax(service_conditions_1['Fl'], ff_liq, service_conditions_1['iPres'],
                      service_conditions_1['vPres'])
    # chokedP = selectDelP(service_conditions_1['Fl'], service_conditions_1['cPres'],
    #                      service_conditions_1['iPres'],
    #                      service_conditions_1['vPres'], service_conditions_1['oPres'])

    # noise and velocities
    # Liquid Noise - need flowrate in kg/s, valves in m, density in kg/m3, pressure in pa
    # convert form data in units of noise formulae
    valveDia_lnoise = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form, 'm', 1000)
    iPipeDia_lnoise = meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'm',
                                            1000)
    oPipeDia_lnoise = meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form, 'm',
                                            1000)
    seat_dia_lnoise = meta_convert_P_T_FR_L('L', seatDia, seatDiaUnit, 'm',
                                            1000)
    inletPipeDia_v = round(meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                                 1000))

    iPipeSch_lnoise = meta_convert_P_T_FR_L('L', float(thickness_pipe),
                                    'mm', 'm', 1000)
    


    
    flowrate_lnoise = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'kg/hr',
                                            specificGravity * 1000) / 3600
    outletPressure_lnoise = meta_convert_P_T_FR_L('P', outletPressure_form, oPres_unit,
                                                  'pa (a)', 1000)
    inletPressure_lnoise = meta_convert_P_T_FR_L('P', inletPressure_form, iPres_unit,
                                                 'pa (a)', 1000)
    vPres_lnoise = meta_convert_P_T_FR_L('P', vaporPressure, vPres_unit, 'pa (a)', 1000)    
    # print(f"3 press: {outletPressure_lnoise, inletPressure_lnoise, vPres_lnoise}")
    # service conditions for 4 inch vale with 8 as line size. CVs need to be changed
    sc_liq_sizing = {'valveDia': valveDia_lnoise, 'ratedCV': ratedCV, 'reqCV': result, 'FL': xt_fl,
                     'FD': 0.42,
                     'iPipeDia': iPipeDia_lnoise, 'iPipeUnit': 'm', 'oPipeDia': oPipeDia_lnoise,
                     'oPipeUnit': 'm',
                     'internalPipeDia': oPipeDia_lnoise,
                     'inPipeDiaUnit': 'm', 'pipeWallThickness': iPipeSch_lnoise, 'speedSoundPipe': sosPipe,
                     'speedSoundPipeUnit': 'm/s',
                     'densityPipe': densityPipe, 'densityPipeUnit': 'kg/m3', 'speedSoundAir': 343,
                     'densityAir': 1293,
                     'massFlowRate': flowrate_lnoise, 'massFlowRateUnit': 'kg/s',
                     'iPressure': inletPressure_lnoise,
                     'iPresUnit': 'pa',
                     'oPressure': outletPressure_lnoise,
                     'oPresUnit': 'pa', 'vPressure': vPres_lnoise, 'densityLiq': specificGravity * 1000,
                     'speedSoundLiq': 1400,
                     'rw': rw_noise,
                     'seatDia': seat_dia_lnoise,
                     'fi': 8000}

    sc_1 = sc_liq_sizing
    try:
        summation = Lpe1m(sc_1['fi'], sc_1['FD'], sc_1['reqCV'], sc_1['iPressure'], sc_1['oPressure'],
                            sc_1['vPressure'],
                            sc_1['densityLiq'], sc_1['speedSoundLiq'], sc_1['massFlowRate'], sc_1['rw'],
                            sc_1['FL'],
                            sc_1['seatDia'], sc_1['valveDia'], sc_1['densityPipe'], sc_1['pipeWallThickness'],
                            sc_1['speedSoundPipe'],
                            sc_1['densityAir'], sc_1['internalPipeDia'], sc_1['speedSoundAir'],
                            sc_1['speedSoundPipe'])
    except:
        summation = 56
    

    # Power Level
    print(f'POWERLEVEL {oPres_unit}')
    outletPressure_p = meta_convert_P_T_FR_L('P', outletPressure_form, oPres_unit,
                                             'psia (a)', specificGravity * 1000)
    inletPressure_p = meta_convert_P_T_FR_L('P', inletPressure_form, iPres_unit,
                                            'psia (a)', specificGravity * 1000)
    print(f'B4PLEVEL')
    # pLevel = power_level_liquid(inletPressure_p, outletPressure_p, specificGravity, result)
    try:
        pLevel = mechanicalPower(sc_1['massFlowRate'], sc_1['FL'], sc_1['iPressure'], sc_1['oPressure'],
                            sc_1['vPressure'], sc_1['densityLiq'])
    except:
        flash('Vapour pressure should not be greater than InletPressure')
        pLevel = 1
    print(f'PLEVEL {pLevel}')
    # convert flowrate and dias for velocities
    

    # convert flowrate and dias for velocities
    flowrate_v = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'm3/hr',
                                       1000)
    inletPipeDia_v = round(meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                                 1000))
    outletPipeDia_v = round(meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form, 'inch',
                                                  1000))
    vSize_v = round(meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                          'inch', specificGravity * 1000))

    # convert pressure for tex, p in bar, l in in
    inletPressure_v = meta_convert_P_T_FR_L('P', inletPressure_form, iPres_unit, 'psia (a)',
                                            1000)
    outletPressure_v = meta_convert_P_T_FR_L('P', outletPressure_form, oPres_unit, 'psia (a)',
                                             1000)
    v_det_element = valve_element
    trim_type_element = db.session.query(trimType).filter_by(id=v_det_element.trimTypeId).first()
    trimtype = trim_type_element.name
    if trimtype == 'contour':
        t_caps = 'Contoured'
    elif trimtype == 'ported':
        t_caps = 'Cage'
    else:
        t_caps = trimtype

    # try:
    tEX = trimExitVelocity(inletPressure_v, outletPressure_v, specificGravity, t_caps,
                        'other')
    print("kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk tex done")
    # except:
    #     tEX = 0
    flow_character = v_det_element.flowCharacter__.name.lower()
    # new trim exit velocity
    # for port area, travel filter not implemented
    port_area_ = port_area_
   

    if port_area_:
        port_area = float(port_area_.area)
    else:
        port_area = 1
    # tex_ = tex_new(result, ratedCV, port_area, flowrate_v / 3600, inletPressure_form, inletPressure_form, 1, 8314,
    #                inletTemp_form, 'Liquid')
    tex_ = trimExitVelocityLiquid(inletPressure_v, outletPressure_v, trimtype, specificGravity)

    # ipipeSch_v = meta_convert_P_T_FR_L('L', float(iPipeSch_form), iPipeSchUnit_form,
    #                                    'inch',
    #                                    1000)
    # opipeSch_v = meta_convert_P_T_FR_L('L', float(oPipeSch_form), oPipeSchUnit_form,
    #                                    'inch',
    #                                    1000)
    # iVelocity, oVelocity, pVelocity = getVelocity(flowrate_v, inletPipeDia_v,
    #                                               outletPipeDia_v,
    #                                               vSize_v)
    # print(flowrate_v, (inletPipeDia_v - ipipeSch_v),
    #       (outletPipeDia_v - opipeSch_v),
    #       vSize_v)
    try:
        i_pipearea_element = i_pipearea_element
        area_in2 = float(i_pipearea_element.area)
        a_i = 0.00064516 * area_in2
        iVelocity = flowrate_v / (3600 * a_i)

        o_pipearea_element = db.session.query(pipeArea).filter_by(nominalPipeSize=float(outletPipeDia_v),
                                                                schedule=oSch).first()
        print(f"oPipedia: {outletPipeDia_v}, sch: {oSch}")
        area_in22 = float(o_pipearea_element.area)
        a_o = 0.00064516 * area_in22
        oVelocity = flowrate_v / (3600 * a_o)
    except:
        a_i = 0.00064516 * 0.074
        iVelocity = flowrate_v / (3600 * a_i)
        a_o = 0.00064516 * 0.074
        oVelocity = flowrate_v / (3600 * a_o)

   
    

    valve_element_current = valve_element
    rating_current = valve_element_current.rating
    valvearea_element = valvearea_element
    if valvearea_element:
        v_area_in = float(valvearea_element.area)
        v_area = 0.00064516 * v_area_in
    else:
        v_area = 0.00064516 * 1
    pVelocity = flowrate_v / (3600 * v_area)

    data = {'cv': round(result, 3),
            'percent': 80,
            'spl': round(summation, 3),
            'iVelocity': iVelocity,
            'oVelocity': round(oVelocity, 3), 'pVelocity': round(pVelocity, 3), 'choked': round(chokedP, 3),
            'texVelocity': round(tEX, 3)}

    units_string = f"{seatDia}+{seatDiaUnit}+{sosPipe}+{densityPipe}+{rw_noise}+{fl_unit_form}+{iPresUnit_form}+{oPresUnit_form}+{vPresUnit_form}+{cPresUnit_form}+{iPipeUnit_form}+{oPipeUnit_form}+{vSizeUnit_form}+mm+mm+{iTempUnit_form}+sg"
    # update valve size in item
    size_in_in = int(round(meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form, 'inch', 1000)))
    # load case data with item ID
    # get valvetype - kc requirements
    v_det_element = valve_element
    valve_type_ = v_det_element.style.name
    trim_type_element = db.session.query(trimType).filter_by(id=v_det_element.trimTypeId).first()
    trimtype = trim_type_element.name
    outletPressure_psia = meta_convert_P_T_FR_L('P', outletPressure_form, oPres_unit,
                                                'psia (a)', 1000)
    inletPressure_psia = meta_convert_P_T_FR_L('P', inletPressure_form, iPres_unit,
                                               'psia (a)', 1000)
    dp_kc = inletPressure_psia - outletPressure_psia

    print(f"kc inputs: {size_in_in}, {trimtype}, {dp_kc}, {valve_type_}, {xt_fl},")
    # Kc = getKCValue(size_in_in, trimtype, dp_kc, valve_type_.lower(), xt_fl)
    Kc = getKc(size_in_in, trimtype, dp_kc, valve_type_, xt_fl)
    print(f"kc inputs: {size_in_in}, {trimtype}, {dp_kc}, {valve_type_.lower()}, {xt_fl}, {Kc}")

    # get other req values - Ff, Kc, Fd, Flp, Reynolds Number
    Ff_liq = round(FF(service_conditions_1['vPres'], service_conditions_1['cPres']), 2)
    Fd_liq = service_conditions_1['FD']
    FLP_liq = flP(result_1, service_conditions_1['valveDia'],
                  service_conditions_1['iPipeDia'], N2_val,
                  service_conditions_1['Fl'])
    RE_number = reynoldsNumber(N4_val, service_conditions_1['FD'], service_conditions_1['flowrate'],
                               service_conditions_1['viscosity'], service_conditions_1['Fl'], N2_val,
                               service_conditions_1['iPipeDia'], N1_val, service_conditions_1['iPres'],
                               service_conditions_1['oPres'],
                               service_conditions_1['sGravity'])
    fp_liq = fP(result_1, service_conditions_1['valveDia'],
                service_conditions_1['iPipeDia'], service_conditions_1['oPipeDia'], N2_val)
    if chokedP == (service_conditions_1['iPres'] - service_conditions_1['oPres']):
        ff = 0.96
    else:
        ff = round(ff_liq, 3)

    vp_ar = meta_convert_P_T_FR_L('P', vaporPressure, vPres_unit, iPres_unit, 1000)


        
    application_ratio = (inletPressure_form - outletPressure_form) / (inletPressure_form - vp_ar)
    if round(application_ratio, 3) < 0:
        application_ratio = 1 


    print(
        f"AR facts: {inletPressure_form}, {outletPressure_form}, {inletPressure_form}, {vp_ar}, {vaporPressure}, {vPres_unit}")
    other_factors_string = f"{ff}+{Kc}+{Fd_liq}+{FLP_liq}+{RE_number}+{fp_liq}+{round(application_ratio, 3)}+{ratedCV}"

    result_list = [flowrate_form, inletPressure_form, outletPressure_form, inletTemp_form, specificGravity,
                   vaporPressure, viscosity, None,
                   valveSize_form, other_factors_string, round(result, 3), data['percent'],
                   round(summation, 3), round(iVelocity, 3),
                   round(oVelocity, 3), round(pVelocity, 3),
                   round(chokedP, 4), xt_fl, 1, tex_, pLevel, units_string, fluidName, "Liquid",
                   criticalPressure_form, inletPipeDia_form,
                   outletPipeDia_form, iSch, oSch,
                   item_selected]
    # print(f'HHHHHHHHHHHHVVVSSS {fl_unit_form},{' '.join(iPresUnit_form)}')
    # iPressureUnit = ' '.join(iPresUnit_form)
    # oPressureUnit = ' '.join(oPresUnit_form)
    # vPressureUnit = ' '.join(vPresUnit_form)
    # cPressureUnit = ' '.join(cPresUnit_form)
    result_dict = {
        'flowrate': flowrate_form,
        'fl_unit_form':fl_unit_form,
        'inletPressure':inletPressure_form,
        'iPresUnit_form':iPresUnit_form,
        'outletPressure': outletPressure_form,
        'oPresUnit_form': oPresUnit_form,
        'inletTemp': inletTemp_form,
        'iTempUnit_form':iTempUnit_form,
        'specificGravity': specificGravity,
        'vaporPressure': vaporPressure_form,
        'vPresUnit_form': vPresUnit_form,
        'kinematicViscosity': viscosity,
        'valveSize': valveSize_form,
        'vSizeUnit_form':vSizeUnit_form,
        'fd': Fd_liq,
        'Ff': ff,
        'Fp': fp_liq,
        'Flp': FLP_liq,
        'ratedCv': ratedCV,
        'ar': round(application_ratio, 3),
        'kc': Kc,
        'reNumber': RE_number,
        'calculatedCv': round(result, 3),
        'openingPercentage': data['percent'],
        'spl': round(summation, 3),
        'pipeInVel': round(iVelocity, 3),
        'pipeOutVel': round(oVelocity, 3),
        'valveVel': round(pVelocity, 3),
        'chokedDrop': round(chokedP, 4),
        'fl': xt_fl,
        'tex': tex_,
        'powerLevel': pLevel,
        'seatDia': seatDia,
        'criticalPressure': criticalPressure_form,
        'cPressureUnit':cPresUnit_form,
        'inletPipeSize': inletPipeDia_form,
        'iPipeUnit_form':iPipeUnit_form,
        'outletPipeSize': outletPipeDia_form,
        'oPipeUnit_form': oPipeUnit_form
        }
    print(f'RESULT {result_dict}')
    return result_dict


# TODO - GAS SIZING


def x_gas(inletPressure, outletPressure):
    result = (inletPressure - outletPressure) / inletPressure
    # print(f"x value is: {round(result, 2)}")
    return round(result, 3)


def etaB_gas(valveDia, pipeDia):
    result = 1 - ((valveDia / pipeDia) ** 4)
    return round(result, 3)


def eta1_gas(valveDia, pipeDia):
    result = 0.5 * ((1 - ((valveDia / pipeDia) ** 2)) ** 2)
    return round(result, 3)


def eta2_gas(valveDia, pipeDia):
    result = 1 * ((1 - ((valveDia / pipeDia) ** 2)) ** 2)
    return round(result, 3)


def sigmaEta_gas(valveDia, inletDia, outletDia):
    result = eta1_gas(valveDia, inletDia) + eta2_gas(valveDia, outletDia) + etaB_gas(valveDia, inletDia) - etaB_gas(
        valveDia, outletDia)
    return round(result, 3)


def fP_gas(C, valveDia, inletDia, outletDia, N2_value):
    a = (sigmaEta_gas(valveDia, inletDia, outletDia) / N2_value) * ((C / valveDia ** 2) ** 2)
    print(f"N2: {N2_value}, sigmaeta: {sigmaEta_gas(valveDia, inletDia, outletDia)}")
    result = 1 / math.sqrt(1 + a)
    # print(f"FP value is: {round(result, 2)}")
    return round(result, 2)


# specific heat ratio - gamma
def F_Gamma_gas(gamma):
    result = gamma / 1.4
    # print(f"F-Gamma: {round(result, 5)}")
    return round(result, 5)


def xChoked_gas(gamma, C, valveDia, inletDia, outletDia, xT, N2_value):
    f_gamma = F_Gamma_gas(gamma)
    if valveDia != inletDia:
        fp = fP_gas(C, valveDia, inletDia, outletDia, N2_value)
        etaI = eta1_gas(valveDia, inletDia) + etaB_gas(valveDia, inletDia)
        # print(f"etaI: {round(etaI, 2)}")
        a_ = xT / fp ** 2
        b_ = (xT * etaI * C * C) / (N5_in * (valveDia ** 4))
        xTP = a_ / (1 + b_)
        result = f_gamma * xTP
        # print(f"xChoked1: {round(result, 2)}")
    else:
        result = f_gamma * xT
        # print(f"xChoked2: {round(result, 3)}")
    return round(result, 4)


def xSizing_gas(inletPressure, outletPressure, gamma, C, valveDia, inletDia, outletDia, xT, N2_value):
    result = min(xChoked_gas(gamma, C, valveDia, inletDia, outletDia, xT, N2_value),
                 x_gas(inletPressure, outletPressure))
    # print(f"xSizing: {round(result, 3)}")
    return round(result, 3)


def xTP_gas(xT, C, valveDia, inletDia, outletDia, N2_value):
    etaI = eta1_gas(valveDia, inletDia) + etaB_gas(valveDia, inletDia)
    fp = fP_gas(C, valveDia, inletDia, outletDia, N2_value)
    a_ = xT / fp ** 2
    b_ = xT * etaI * C * C / (N5_in * (valveDia ** 4))
    result = a_ / (1 + b_)
    return round(result, 3)


Cv_globe_4 = [17, 24, 34, 47, 65, 88, 134, 166, 187, 201, 20000000]
Fl_globle_4 = [0.93, 0.9275, 0.92, 0.91, 0.905, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9]

Cv_butterfly_6 = [56, 126, 204, 306, 425, 556, 671, 717, 698, 200000]
Fl_butterfly_6 = [0.97, 0.95, 0.92, 0.9, 0.88, 0.83, 0.79, 0.72, 0.7, 0.67]

Opening = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 100]

Cv1 = Cv_butterfly_6
FL1 = Fl_butterfly_6

def getFL(C):
    a = 0
    while True:
        # print(f"Cv1, C: {Cv1[a], C}")
        if Cv1[a] == C:
            return FL1[a]
        elif Cv1[a] > C:
            break
        else:
            a += 1

    Fllll = FL1[a - 1] - (((Cv1[a - 1] - C) / (Cv1[a - 1] - Cv1[a])) * (FL1[a - 1] - FL1[a]))

    return round(Fllll, 3)

def fLP(C, valveDia, inletDia):
    FL_input = getFL(C)
    a = (FL_input * FL_input / 0.00214) * (eta1(valveDia, inletDia) + etaB(valveDia, inletDia)) * (
            (C / (valveDia * valveDia)) ** 2)
    try:
        output = FL_input / (math.sqrt(1 + a))
    except:
        output = 1
    return output

# Expansion factor
def Y_gas(inletPressure, outletPressure, gamma, C, valveDia, inletDia, outletDia, xT, N2_value):
    f_gamma = F_Gamma_gas(gamma)
    a = 1 - ((xSizing_gas(inletPressure, outletPressure, gamma, C, valveDia, inletDia, outletDia, xT, N2_value) / (
            3 * xChoked_gas(gamma, C, valveDia, inletDia, outletDia, xT, N2_value))))
    # print(
    #     f"rhs for y: {(xSizing_gas(inletPressure, outletPressure, gamma, C, valveDia, inletDia, outletDia, xT, N2_value) / (3 * xChoked_gas(gamma, C, valveDia, inletDia, outletDia, xT, N2_value)))}")
    result_ch = min(xChoked_gas(gamma, C, valveDia, inletDia, outletDia, xT, N2_value),
                    x_gas(inletPressure, outletPressure))
    if result_ch == xChoked_gas(gamma, C, valveDia, inletDia, outletDia, xT, N2_value):
        result = (2 / 3)
    else:
        result = a
    # result = a

    # print(f"Y value is: {round(result, 3)}")

    return round(result, 7)




def Cv_gas(inletPressure, outletPressure, gamma, C, valveDia, inletDia, outletDia, xT, temp, compressibilityFactor,
           flowRate, sg, sg_, N2_value):
    # sg_ = int(input("Which value do you want to give? \nVolumetric Flow - Specific Gravity (1) \nVolumetric Flow - "
    #                 "Molecular Weight (2)\nMass Flow - Specific Weight (3)\nMass Flow - Molecular Weight (4)\nSelect "
    #                 "1 0r 2 0r 3 or 4: "))

    sg_ = sg_

    # if sg_ == 1:
    #     Gg = int(input("Give value of Gg: "))
    #     sg = 0.6
    # elif sg_ == 2:
    #     M = int(input("Give value of M: "))
    #     sg = M
    # elif sg_ == 3:
    #     gamma_1 = int(input("Give value of Gamma1: "))
    #     sg = gamma_1
    # else:
    #     M = int(input("Give value of M: "))
    #     sg = M

    # sg = 1.0434
    sg = sg

    a_ = inletPressure * fP_gas(C, valveDia, inletDia, outletDia, N2_value) * Y_gas(inletPressure, outletPressure,
                                                                                    gamma, C,
                                                                                    valveDia,
                                                                                    inletDia, outletDia, xT, N2_value)
    b_ = temp * compressibilityFactor
    x_ = x_gas(inletPressure, outletPressure)
    x__ = xSizing_gas(inletPressure, outletPressure, gamma, C, valveDia, inletDia, outletDia, xT, N2_value)
    print(f'sg_ value: {sg_}')
    if sg_ == 1:
        A = flowRate / (
                N7_60_scfh_psi_F * inletPressure * fP_gas(C, valveDia, inletDia, outletDia, N2_value) * Y_gas(
            inletPressure,
            outletPressure,
            gamma, C,
            valveDia,
            inletDia,
            outletDia,
            xT, N2_value) * math.sqrt(
            x__ / (sg * temp * compressibilityFactor)))
        # return round(A, 3)

    elif sg_ == 2:
        A = flowRate / (N9_O_m3hr_kPa_C * a_ * math.sqrt(x__ / (sg * b_)))
        print('gas sizing eq2 input in m3hr kpa and C:')
        print(flowRate, N9_O_m3hr_kPa_C, a_, x_, x__, sg, temp, compressibilityFactor)
        # return A

    elif sg_ == 3:
        A = flowRate / (
                N6_lbhr_psi_lbft3 * fP_gas(C, valveDia, inletDia, outletDia, N2_value) * Y_gas(inletPressure,
                                                                                               outletPressure,
                                                                                               gamma, C, valveDia,
                                                                                               inletDia, outletDia,
                                                                                               xT,
                                                                                               N2_value) * math.sqrt(
            x__ * sg * inletPressure))
        # return A

    else:
        print(f"flowrate, nx_kghr_bar_K, a_, x__, sg, b_")
        print(flowRate, N8_kghr_bar_K, a_, x__, sg, b_)
        A = flowRate / (N8_kghr_bar_K * a_ * math.sqrt((x__ * sg) / b_))
        # return A
    fk = F_Gamma_gas(gamma)
    x_choked = xChoked_gas(gamma, C, valveDia, inletDia, outletDia, xT, N2_value)
    y = Y_gas(inletPressure, outletPressure, gamma, C, valveDia, inletDia, outletDia, xT, N2_value)
    xtp = xTP_gas(xT, C, valveDia, inletDia, outletDia, N2_value)
    fp__ = fP_gas(C, valveDia, inletDia, outletDia, N2_value)
    output_list = [round(A, 3), x_, fk, x_choked, y, xT, xtp, fp__]
    return output_list

# flowrate in kg/hr, pressure in pa, density in kg/m3
def power_level_gas(specificHeatRatio, inletPressure, outletPressure, flowrate, density):
    pressureRatio = outletPressure / inletPressure
    specificVolume = 1 / density
    heatRatio = specificHeatRatio / (specificHeatRatio - 1)
    a_ = heatRatio * inletPressure * specificVolume
    b_ = (1 - pressureRatio ** (1 / heatRatio)) * flowrate / 36000000
    c_ = a_ * b_
    return round(c_, 3)



# pressure in psi
def trimExitVelocityGas(inletPressure, outletPressure):
    a__ = (inletPressure - outletPressure) / 0.0214
    a_ = math.sqrt(a__)
    return round(a_, 3)




# Gas sizng outputs
def getOutputsGas(flowrate_form, fl_unit_form, inletPressure_form, iPresUnit_form, outletPressure_form, oPresUnit_form,
                  inletTemp_form,
                  iTempUnit_form, vaporPressure, vPresUnit_form, specificGravity, viscosity, xt_fl,
                  criticalPressure_form,
                  cPresUnit_form,
                  inletPipeDia_form, iPipeUnit_form, iSch, outletPipeDia_form, oPipeUnit_form, oSch, densityPipe,
                  sosPipe,
                  valveSize_form, vSizeUnit_form,
                  seatDia, seatDiaUnit, ratedCV, rw_noise, item_selected, sg_choice, z_factor, sg_vale, 
                  fluidName, i_pipearea_element, valve_element, port_area_):
    flowrate_form, fl_unit_form, inletPressure_form, iPresUnit_form, outletPressure_form, oPresUnit_form, inletTemp_form, iTempUnit_form, vaporPressure, vPresUnit_form, specificGravity, viscosity, xt_fl, criticalPressure_form, cPresUnit_form, inletPipeDia_form, iPipeUnit_form, iSch, outletPipeDia_form, oPipeUnit_form, oSch, densityPipe, sosPipe, valveSize_form, vSizeUnit_form, seatDia, seatDiaUnit, ratedCV, rw_noise, item_selected, z_factor, sg_vale = float(
        flowrate_form), fl_unit_form, float(inletPressure_form), iPresUnit_form, float(
        outletPressure_form), oPresUnit_form, float(inletTemp_form), iTempUnit_form, float(
        vaporPressure), vPresUnit_form, float(specificGravity), float(viscosity), float(xt_fl), float(
        criticalPressure_form), cPresUnit_form, float(inletPipeDia_form), iPipeUnit_form, iSch, float(
        outletPipeDia_form), oPipeUnit_form, oSch, float(densityPipe), float(sosPipe), float(
        valveSize_form), vSizeUnit_form, float(seatDia), seatDiaUnit, float(ratedCV), float(
        rw_noise), item_selected, float(z_factor), float(sg_vale)
    print(f'JJJJJJJJJJJJJJJJJJJGASSSSSSSSGGBB {iPresUnit_form}')
    
    fl_unit = fl_unit_form
    if fl_unit in ['m3/hr', 'scfh', 'gpm']:
        fl_bin = 1
    else:
        fl_bin = 2

    sg_unit = sg_choice
    if sg_unit == 'sg':
        sg_bin = 1
    else:
        sg_bin = 2

    def chooses_gas_fun(flunit, sgunit):
        eq_dict = {(1, 1): 1, (1, 2): 2, (2, 1): 3, (2, 2): 4}
        return eq_dict[(flunit, sgunit)]

    sg__ = chooses_gas_fun(fl_bin, sg_bin)

    inletPipeDia_v = round(meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                                 1000))
    try:

        i_pipearea_element = i_pipearea_element
        thickness_pipe = float(i_pipearea_element.thickness)
    except:
        thickness_pipe = 1.24

    thickness_in = meta_convert_P_T_FR_L('L', thickness_pipe, 'mm', 'inch', 1000)
    print(f'SGG {sg__}')
    if sg__ == 1:
        # to be converted to scfh, psi, R, in
        # 3. Pressure
        inletPressure = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form,
                                              'psia',
                                              1000)
        outletPressure = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                               'psia',
                                               1000)
        # 4. Length
        inletPipeDia = meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                             1000) - 2 * thickness_in
        outletPipeDia = meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form,
                                              'inch',
                                              1000) - 2 * thickness_in
        vSize = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                      'inch', specificGravity * 1000)
        # 1. Flowrate
        flowrate = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'scfh',
                                         1000)
        # 2. Temperature
        inletTemp = meta_convert_P_T_FR_L('T', inletTemp_form, iTempUnit_form, 'R',
                                          1000)
    elif sg__ == 2:
        # to be converted to m3/hr, kPa, C, in
        # 3. Pressure - 2*thickness_in
        inletPressure = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form, 'kpa',
                                              1000)
        outletPressure = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                               'kpa',
                                               1000)
        # 4. Length
        inletPipeDia = meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                             1000) - 2 * thickness_in
        outletPipeDia = meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form,
                                              'inch',
                                              1000) - 2 * thickness_in
        vSize = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                      'inch', specificGravity * 1000)
        # 1. Flowrate
        flowrate = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'm3/hr',
                                         1000)
        # 2. Temperature
        inletTemp = meta_convert_P_T_FR_L('T', inletTemp_form, iTempUnit_form, 'K',
                                          1000)
    elif sg__ == 3:
        # to be converted to lbhr, psi, F, in
        # 3. Pressure
        inletPressure = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form,
                                              'psia',
                                              1000)
        outletPressure = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                               'psia',
                                               1000)
        # 4. Length
        inletPipeDia = meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                             1000) - 2 * thickness_in
        # print(iPipeUnit_form)
        outletPipeDia = meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form,
                                              'inch',
                                              1000) - 2 * thickness_in
        vSize = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                      'inch', specificGravity * 1000)
        # 1. Flowrate
        flowrate = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'lb/hr',
                                         1000)
        # 2. Temperature
        inletTemp = meta_convert_P_T_FR_L('T', inletTemp_form, iTempUnit_form, 'F',
                                          1000)
    else:
        # to be converted to kg/hr, bar, K, in
        # 3. Pressure
        
        inletPressure = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form, 'bar (a)',
                                              1000)
        print(f'InletPressure {inletPressure}')
        outletPressure = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                               'bar (a)',
                                               1000)
        # 4. Length
        inletPipeDia = meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                             1000) - 2 * thickness_in
        outletPipeDia = meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form,
                                              'inch',
                                              1000) - 2 * thickness_in
        vSize = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                      'inch', specificGravity * 1000)
        # 1. Flowrate
        flowrate = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'kg/hr',
                                         1000)
        # 2. Temperature
        inletTemp = meta_convert_P_T_FR_L('T', inletTemp_form, iTempUnit_form, 'K',
                                          1000)

    print(f"dia of pipe: {outletPipeDia}, {inletPipeDia}")

    # python sizing function - gas

    inputDict_4 = {"inletPressure": inletPressure, "outletPressure": outletPressure,
                   "gamma": specificGravity,
                   "C": ratedCV,
                   "valveDia": vSize,
                   "inletDia": inletPipeDia,
                   "outletDia": outletPipeDia, "xT": float(xt_fl),
                   "compressibilityFactor": z_factor,
                   "flowRate": flowrate,
                   "temp": inletTemp, "sg": float(sg_vale), "sg_": sg__}

    print(inputDict_4)

    inputDict = inputDict_4
    N2_val = N2['inch']
    CV__ = Cv_gas(inletPressure=inputDict['inletPressure'], outletPressure=inputDict['outletPressure'],
                  gamma=inputDict['gamma'],
                  C=inputDict['C'], valveDia=inputDict['valveDia'], inletDia=inputDict['inletDia'],
                  outletDia=inputDict['outletDia'], xT=inputDict['xT'],
                  compressibilityFactor=inputDict['compressibilityFactor'],
                  flowRate=inputDict['flowRate'], temp=inputDict['temp'], sg=inputDict['sg'],
                  sg_=inputDict['sg_'], N2_value=N2_val)
    Cv__ = Cv_gas(inletPressure=inputDict['inletPressure'], outletPressure=inputDict['outletPressure'],
                  gamma=inputDict['gamma'],
                  C=CV__[0], valveDia=inputDict['valveDia'], inletDia=inputDict['inletDia'],
                  outletDia=inputDict['outletDia'], xT=inputDict['xT'],
                  compressibilityFactor=inputDict['compressibilityFactor'],
                  flowRate=inputDict['flowRate'], temp=inputDict['temp'], sg=inputDict['sg'],
                  sg_=inputDict['sg_'], N2_value=N2_val)
    Cv1 = Cv__[0]

    xChoked = xChoked_gas(gamma=inputDict['gamma'], C=inputDict['C'], valveDia=inputDict['valveDia'],
                          inletDia=inputDict['inletDia'], outletDia=inputDict['outletDia'],
                          xT=inputDict['xT'], N2_value=N2_val)

    # noise and velocities
    # Liquid Noise - need flowrate in kg/s, valves in m, density in kg/m3, pressure in pa
    inletPressure_gnoise = float(meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form,
                                                       'pa (a)',
                                                       1000))
    outletPressure_gnoise = float(meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                                        'pa (a)',
                                                        1000))
    # vaporPressure_gnoise = meta_convert_P_T_FR_L('P', vaporPressure, vPresUnit_form, 'pa',
    #                                              1000)
    flowrate_gnoise = conver_FR_noise(flowrate_form, fl_unit)
    inletPipeDia_gnoise = meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'm',
                                                specificGravity * 1000)
    outletPipeDia_gnoise = meta_convert_P_T_FR_L('L', outletPipeDia_form, iPipeUnit_form,
                                                 'm',
                                                 specificGravity * 1000)
    size_gnoise = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                        'm', specificGravity * 1000)
    seat_dia_gnoise = meta_convert_P_T_FR_L('L', seatDia, seatDiaUnit, 'm',
                                            1000)
    mw = float(sg_vale)
    if sg_unit == 'sg':
        mw = 22.4 * float(sg_vale)
    elif sg_unit == 'mw':
        mw = float(sg_vale)

    temp_gnoise = meta_convert_P_T_FR_L('T', inletTemp_form, iTempUnit_form, 'K', 1000)
    flp = fLP(Cv1, valveSize_form, inletPipeDia_form)
    fp = fP_gas(Cv1, valveSize_form, inletPipeDia_form, outletPipeDia_form, N2_val)
    sigmeta = sigmaEta_gas(valveSize_form, inletPipeDia_form, outletPipeDia_form)
    flowrate_gv = int(flowrate_form) / 3600
    inlet_density = inletDensity(inletPressure_gnoise, mw, 8314, temp_gnoise)
    # print('inlet density input:')
    # print(inletPressure_gnoise, mw, 8314, temp_gnoise)
    if sigmeta == 0:
        sigmeta = 0.86
    sc_initial_1 = {'valveSize': size_gnoise, 'valveOutletDiameter': outletPipeDia_gnoise,
                    'ratedCV': ratedCV,
                    'reqCV': 175,
                    'No': 6,
                    'FLP': flp,
                    'Iw': 0.181, 'valveSizeUnit': 'm', 'IwUnit': 'm', 'A': 0.00137,
                    'xT': float(xt_fl),
                    'iPipeSize': inletPipeDia_gnoise,
                    'oPipeSize': outletPipeDia_gnoise,
                    'tS': 0.008, 'Di': outletPipeDia_gnoise, 'SpeedOfSoundinPipe_Cs': sosPipe,
                    'DensityPipe_Ps': densityPipe,
                    'densityUnit': 'kg/m3',
                    'SpeedOfSoundInAir_Co': 343, 'densityAir_Po': 1.293, 'atmPressure_pa': 101325,
                    'atmPres': 'pa',
                    'stdAtmPres_ps': 101325, 'stdAtmPres': 'pa', 'sigmaEta': sigmeta, 'etaI': 1.2, 'Fp': fp,
                    'massFlowrate': flowrate_gnoise, 'massFlowrateUnit': 'kg/s',
                    'iPres': inletPressure_gnoise, 'iPresUnit': 'pa',
                    'oPres': outletPressure_gnoise, 'oPresUnit': 'pa', 'inletDensity': 5.3,
                    'iAbsTemp': temp_gnoise,
                    'iAbsTempUnit': 'K',
                    'specificHeatRatio_gamma': specificGravity, 'molecularMass': mw, 'mMassUnit': 'kg/kmol',
                    'internalPipeDia': inletPipeDia_gnoise,
                    'aEta': -3.8, 'stp': 0.2, 'R': 8314, 'RUnit': "J/kmol x K", 'fs': 1}

    sc_initial_2 = {'valveSize': size_gnoise, 'valveOutletDiameter': outletPipeDia_gnoise,
                    'ratedCV': ratedCV,
                    'reqCV': Cv1, 'No': 1,
                    'FLP': flp,
                    'Iw': 0.181, 'valveSizeUnit': 'm', 'IwUnit': 'm', 'A': 0.00137,
                    'xT': float(xt_fl),
                    'iPipeSize': inletPipeDia_gnoise,
                    'oPipeSize': outletPipeDia_gnoise,
                    'tS': 0.008, 'Di': inletPipeDia_gnoise, 'SpeedOfSoundinPipe_Cs': sosPipe,
                    'DensityPipe_Ps': densityPipe,
                    'densityUnit': 'kg/m3',
                    'SpeedOfSoundInAir_Co': 343, 'densityAir_Po': 1.293, 'atmPressure_pa': 101325,
                    'atmPres': 'pa',
                    'stdAtmPres_ps': 101325, 'stdAtmPres': 'pa', 'sigmaEta': sigmeta, 'etaI': 1.2,
                    'Fp': 0.98,
                    'massFlowrate': flowrate_gv, 'massFlowrateUnit': 'kg/s', 'iPres': inletPressure_gnoise,
                    'iPresUnit': 'pa',
                    'oPres': outletPressure_gnoise, 'oPresUnit': 'pa', 'inletDensity': inlet_density,
                    'iAbsTemp': temp_gnoise,
                    'iAbsTempUnit': 'K',
                    'specificHeatRatio_gamma': specificGravity, 'molecularMass': mw,
                    'mMassUnit': 'kg/kmol',
                    'internalPipeDia': inletPipeDia_gnoise,
                    'aEta': -3.8, 'stp': 0.2, 'R': 8314, 'RUnit': "J/kmol x K", 'fs': 1}

    sc_initial = sc_initial_2
    # print(sc_initial)
    try:
        summation1 = lpae_1m(sc_initial['specificHeatRatio_gamma'], sc_initial['iPres'], sc_initial['oPres'],
                            sc_initial['FLP'],
                            sc_initial['Fp'],
                            sc_initial['inletDensity'], sc_initial['massFlowrate'], sc_initial['aEta'],
                            sc_initial['R'],
                            sc_initial['iAbsTemp'],
                            sc_initial['molecularMass'], sc_initial['oPipeSize'],
                            sc_initial['internalPipeDia'], sc_initial['stp'],
                            sc_initial['No'],
                            sc_initial['A'], sc_initial['Iw'], sc_initial['reqCV'],
                            sc_initial['SpeedOfSoundinPipe_Cs'],
                            sc_initial['SpeedOfSoundInAir_Co'],
                            sc_initial['valveSize'], sc_initial['tS'], sc_initial['fs'],
                            sc_initial['atmPressure_pa'],
                            sc_initial['stdAtmPres_ps'], sc_initial['DensityPipe_Ps'], -3.002)
    except:
        summation1 = 80

    print(f"gas summation: {summation1}")
    # summation1 = 97

    # convert flowrate and dias for velocities
    flowrate_v = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'm3/hr',
                                       mw / 22.4)
    inletPipeDia_v = round(meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                                 1000))
    outletPipeDia_v = round(meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form, 'inch',
                                                  1000))

    size_v = round(meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                         'inch', specificGravity * 1000))

    # get gas velocities
    inletPressure_gv = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form, 'pa (a)',
                                             1000)
    outletPressure_gv = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form, 'pa (a)',
                                              1000)
    flowrate_gv = flowrate_form / 3600
    print(f'flowrate_gv: {flowrate_gv}')
    inletPipeDia_gnoise = meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'm',
                                                specificGravity * 1000)
    outletPipeDia_gnoise = meta_convert_P_T_FR_L('L', outletPipeDia_form, iPipeUnit_form,
                                                 'm',
                                                 specificGravity * 1000)
    size_gnoise = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                        'm', specificGravity * 1000)
    temp_gnoise = meta_convert_P_T_FR_L('T', inletTemp_form, iTempUnit_form, 'K', 1000)

    gas_vels = getGasVelocities(sc_initial['specificHeatRatio_gamma'], inletPressure_gv, outletPressure_gv,
                                8314, temp_gnoise, mw, flowrate_gv,
                                size_gnoise, inletPipeDia_gnoise, outletPipeDia_gnoise)

    # Power Level
    # getting fr in lb/s
    flowrate_p = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'kg/hr',
                                       specificGravity * 1000)
    inletPressure_p = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form, 'pa (a)',
                                            1000)
    outletPressure_p = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                             'pa (a)',
                                             1000)
    pLevel = power_level_gas(specificGravity, inletPressure_p, outletPressure_p, flowrate_p, gas_vels[9])
    pLevel = getPowerLevelGas(sc_initial['iPres'], sc_initial['oPres'], sc_initial['specificHeatRatio_gamma'], 
                              sc_initial['FLP'], sc_initial['Fp'],
                            sc_initial['inletDensity'], sc_initial['massFlowrate'])
    

    # print(sc_initial['specificHeatRatio_gamma'], inletPressure_gv, outletPressure_gv, 8314,
    #       temp_gnoise, mw, flowrate_gv, size_gnoise,
    #       inletPipeDia_gnoise, outletPipeDia_gnoise)

    # convert pressure for tex, p in bar, l in in
    inletPressure_v = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form, 'pa (a)',
                                            1000)
    outletPressure_v = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form, 'pa (a)',
                                             1000)
    # get tex pressure in psi
    inletPressure_tex = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form, 'psia (a)',
                                              1000)
    outletPressure_tex = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form, 'psia (a)',
                                               1000)

    tEX = trimExitVelocityGas(inletPressure_tex, outletPressure_tex) / 3.281
    print(
        f"tex: {tEX}, {inletPressure_tex}, {outletPressure_tex}, {inletPressure_tex - outletPressure_tex}")
    # print(summation1)
    iVelocity = gas_vels[6]
    oVelocity = gas_vels[7]
    pVelocity = gas_vels[8]

    data = {'cv': round(Cv1, 3),
            'percent': 83,
            'spl': round(summation1, 3),
            'iVelocity': round(iVelocity, 3),
            'oVelocity': round(oVelocity, 3), 'pVelocity': round(pVelocity, 3), 'choked': round(xChoked, 4),
            'texVelocity': round(tEX, 3)}

    units_string = f"{seatDia}+{seatDiaUnit}+{sosPipe}+{densityPipe}+{z_factor}+{fl_unit_form}+{iPresUnit_form}+{oPresUnit_form}+{oPresUnit_form}+{oPresUnit_form}+{iPipeUnit_form}+{oPipeUnit_form}+{vSizeUnit_form}+mm+mm+{iTempUnit_form}+{sg_choice}"
    # update valve size in item
    size_in_in = int(round(meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form, 'inch', 1000)))
    # size_id = db.session.query(cvTable).filter_by(valveSize=size_in_in).first()
    # # print(size_id)
    # item_selected.size = size_id
    # load case data with item ID
    # get valvetype - kc requirements
    v_det_element = valve_element
    valve_type_ = v_det_element.style.name
    trim_type_element = db.session.query(trimType).filter_by(id=v_det_element.trimTypeId).first()
    trimtype = trim_type_element.name
    outletPressure_psia = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                                'psia (a)', 1000)
    inletPressure_psia = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form,
                                               'psia (a)', 1000)
    dp_kc = inletPressure_psia - outletPressure_psia
    # Kc = getKCValue(size_in_in, trimtype, dp_kc, valve_type_.lower(), xt_fl)
    Kc = getKc(size_in_in, trimtype, dp_kc, valve_type_, xt_fl)

    # get other req values - Ff, Kc, Fd, Flp, Reynolds Number
    Ff_gas = 0.96
    Fd_gas = 1
    xtp = xTP_gas(inputDict['xT'], inputDict['C'], inputDict['valveDia'], inputDict['inletDia'],
                  inputDict['outletDia'], N2_val)
    N1_val = 0.865
    N4_val = 76000
    inletPressure_re = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form, 'bar (a)',
                                             1000)
    outletPressure_re = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form, 'bar (a)',
                                              1000)
    inletPipeDia_re = round(meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'mm',
                                                  1000))
    flowrate_re = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'm3/hr',
                                        mw / 22.4)
    RE_number = reynoldsNumber(N4_val, Fd_gas, flowrate_re,
                               1, 0.9, N2_val,
                               inletPipeDia_re, N1_val, inletPressure_re,
                               outletPressure_re,
                               mw / 22400)
    fpgas = fP(inputDict['C'], inputDict['valveDia'], inputDict['inletDia'], inputDict['outletDia'], N2_val)

    mac_sonic_list = [gas_vels[0], gas_vels[1], gas_vels[2],
                      gas_vels[3], gas_vels[4], gas_vels[5], gas_vels[9]]

    vp_ar = meta_convert_P_T_FR_L('P', vaporPressure, iPresUnit_form, iPresUnit_form, 1000)
    application_ratio = (inletPressure_form - outletPressure_form) / (inletPressure_form - vp_ar)
    # other_factors_string = f"{Ff_gas}+{Kc}+{Fd_gas}+{xtp}+{RE_number}+{fpgas}"
    # CV___ = [cv, x_, fk, x_choked, y, xT, xtp, fp__]
    other_factors_string = f"{Cv__[1]}+{Cv__[2]}+{Cv__[3]}+{Cv__[4]}+{Cv__[5]}+{Cv__[6]}+{Cv__[7]}+{Fd_gas}+{RE_number}+{Kc}+{mac_sonic_list[0]}+{mac_sonic_list[1]}+{mac_sonic_list[2]}+{mac_sonic_list[3]}+{mac_sonic_list[4]}+{mac_sonic_list[5]}+{mac_sonic_list[6]}+{round(application_ratio, 3)}+{z_factor}+{ratedCV}"
    # print(other_factors_string)
    valve_det_element = valve_element
    # tex new
    # flow_character = getFlowCharacter(valve_det_element.flowCharacter__.name)
        # new trim exit velocity
        # for port area, travel filter not implemented
    try:
        port_area_ = port_area_
    except:
        port_area_ = None

    if port_area_:
        port_area = float(port_area_.area)
    else:
        port_area = 1
    tex_ = tex_new(Cv1, ratedCV, port_area, flowrate_re / 3600, inletPressure_v, outletPressure_v, mw,
                   8314, temp_gnoise, 'Gas')

    result_list = [flowrate_form, inletPressure_form, outletPressure_form, inletTemp_form, specificGravity,
                   vaporPressure, viscosity, float(sg_vale), valveSize_form, other_factors_string,
                   round(Cv1, 3), data['percent'], data['spl'], data['iVelocity'], data['oVelocity'],
                   data['pVelocity'], round(data['choked'] * inletPressure_form, 3), float(xt_fl), 1, tex_,
                   pLevel, units_string, fluidName, "Gas", round(criticalPressure_form, 3), inletPipeDia_form,
                   outletPipeDia_form, iSch, oSch, item_selected]
    
    # f"+{Fd_gas}+{RE_number}+{Kc}+{mac_sonic_list[0]}+{mac_sonic_list[1]}+{mac_sonic_list[2]}+{mac_sonic_list[3]}+{mac_sonic_list[4]}+{mac_sonic_list[5]}+{mac_sonic_list[6]}+{round(application_ratio, 3)}+{z_factor}+{ratedCV}"

    result_dict = {
        'flowrate': flowrate_form,
        'fl_unit_form':fl_unit_form,
        'inletPressure':inletPressure_form,
        'iPresUnit_form':iPresUnit_form,
        'outletPressure': outletPressure_form,
        'oPresUnit_form': oPresUnit_form,
        'inletTemp': inletTemp_form,
        'iTempUnit_form':iTempUnit_form,
        'specificGravity': specificGravity,
        'vaporPressure': vaporPressure,
        'vPresUnit_form': vPresUnit_form,
        'kinematicViscosity': viscosity,
        'molecularWeight': float(sg_vale),
        'valveSize': valveSize_form,
        'vSizeUnit_form':vSizeUnit_form,
        'fk': Cv__[2],
        'y': Cv__[4],
        'xt': float(xt_fl),
        'xtp': Cv__[6],
        'fd': Fd_gas,
        'Fp': Cv__[7],
        'ratedCv': ratedCV,
        'ar': round(application_ratio, 3),
        'kc': Kc,
        'reNumber': RE_number,
        'calculatedCv': round(Cv1, 3),
        'openingPercentage': data['percent'],
        'spl': data['spl'],
        'pipeInVel': data['iVelocity'],
        'pipeOutVel': data['oVelocity'],
        'valveVel': data['pVelocity'],
        'chokedDrop': round(data['choked'] * inletPressure_form, 3),
        'fl': xt_fl,
        'tex': tex_,
        'powerLevel': pLevel,
        'seatDia': seatDia,
        'criticalPressure': criticalPressure_form,
        'cPressureUnit':cPresUnit_form,
        'inletPipeSize': inletPipeDia_form,
        'iPipeUnit_form':iPipeUnit_form,
        'outletPipeSize': outletPipeDia_form,
        'oPipeUnit_form': oPipeUnit_form,
        'machNoUp': mac_sonic_list[0],
        'machNoDown': mac_sonic_list[1],
        'machNoVel': mac_sonic_list[2],
        'sonicVelUp': mac_sonic_list[3],
        'sonicVelDown': mac_sonic_list[4],
        'sonicVelValve': mac_sonic_list[5],
        'outletDensity': mac_sonic_list[6],
        'valveSize': valveSize_form
        }

    return result_dict


@app.route('/update_fluidState/proj-<proj_id>/item-<item_id>/<fs_id>', methods=['GET', 'POST'])
def updateFluidState(proj_id, item_id, fs_id):
    item_selected = getDBElementWithId(itemMaster, item_id)
    valve_element = db.session.query(valveDetailsMaster).filter_by(item=item_selected).first()
    fluid_state = getDBElementWithId(fluidState, fs_id)
    print(fluid_state.name)
    valve_element.state = fluid_state
    db.session.commit()
    return redirect(url_for('valveSizing', item_id=item_id, proj_id=proj_id))


def liqSizing(flowrate_form, specificGravity, inletPressure_form, outletPressure_form, vaporPressure,
              criticalPressure_form, outletPipeDia_form, inletPipeDia_form, valveSize_form, inletTemp_form, ratedCV,
              xt_fl, viscosity, seatDia, seatDiaUnit, sosPipe, densityPipe, rw_noise, item_selected, fl_unit_form,
              iPresUnit_form, oPresUnit_form, vPresUnit_form, cPresUnit_form, iPipeUnit_form, oPipeUnit_form,
              vSizeUnit_form,
              iSch, iPipeSchUnit_form, oSch, oPipeSchUnit_form, iTempUnit_form, open_percent, fd, travel, 
              rated_cv_tex, fluidName, cv_table, i_pipearea_element, valve_element, port_area_, valvearea_element):
    # check whether flowrate, pres and l are in correct units
    inletPipeDia_v = round(meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                                 1000))
    
    try:

        i_pipearea_element = i_pipearea_element
        thickness_pipe = float(i_pipearea_element.thickness)
    except:
        thickness_pipe = 1.24
    print(f"thickness: {thickness_pipe}")
    print(f' UNITSFORVALVEDATA {flowrate_form},{fl_unit_form},{inletPressure_form},{iPresUnit_form},{outletPressure_form},{oPresUnit_form},{inletTemp_form},{iTempUnit_form},{vaporPressure},{vPresUnit_form},{criticalPressure_form},{cPresUnit_form},{inletPipeDia_form},{iPipeUnit_form},{outletPipeDia_form},{oPipeUnit_form},{valveSize_form},{vSizeUnit_form}')
    # 1. flowrate
    if fl_unit_form:
        flowrate_liq = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form,
                                             'm3/hr',
                                             specificGravity * 1000)
        fr_unit = 'm3/hr'
    else:
        fr_unit = fl_unit_form
        flowrate_liq = flowrate_form

    # 2. Pressure
    # A. inletPressure
    # iPresUnit_form = iPresUnit_form.split(' ')
    # if iPresUnit_form[1] == '(g)':
    #     inletPressure_form_new = meta_convert_g_to_a(inletPressure_form,iPresUnit_form[0])
    #     print(f'Intermediates {inletPressure_form_new}')
    # else:
    #     inletPressure_form_new = inletPressure_form
    
    # if iPresUnit_form:
    inletPressure_liq = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form,
                                                'bar (a)', specificGravity * 1000)
    iPres_unit = 'bar (a)'
    # else:
    #     iPres_unit = iPresUnit_form[0]
    #     inletPressure_liq = inletPressure_form

    # B. outletPressure
    # oPresUnit_form = oPresUnit_form.split(' ')
    # if oPresUnit_form[1] == '(g)':
    #     outletPressure_form_new = meta_convert_g_to_a(outletPressure_form,oPresUnit_form[0])
    #     print(f'Intermediates {outletPressure_form_new}')
    # else:
        # outletPressure_form_new = outletPressure_form
    # if oPresUnit_form:
    outletPressure_liq = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                                'bar (a)', specificGravity * 1000)
    oPres_unit = 'bar (a)'
    # else:
    #     oPres_unit = oPresUnit_form[0]
    #     outletPressure_liq = outletPressure_form

    # C. vaporPressure
    # vPresUnit_form = vPresUnit_form.split(' ')
    # if vPresUnit_form[1] == '(g)':
    #     vaporPressure_form_new = meta_convert_g_to_a(vaporPressure,vPresUnit_form[0])
    #     print(f'Intermediates {vaporPressure_form_new}')
    # else:
    #     vaporPressure_form_new = vaporPressure
    
    # if vPresUnit_form:
    vaporPressure = meta_convert_P_T_FR_L('P', vaporPressure, vPresUnit_form, 'bar (a)',
                                            specificGravity * 1000)
    vPres_unit = 'bar (a)'
    # else:
    #     vPres_unit = vPresUnit_form[0]

    # D. Critical Pressure
    # cPresUnit_form = cPresUnit_form.split(' ')
    # if cPresUnit_form[1] == '(g)':
    #     criticalPressure_form_new = meta_convert_g_to_a(criticalPressure_form,cPresUnit_form[0])
    #     print(f'Intermediates {criticalPressure_form_new}')
    # else:
    #     criticalPressure_form_new = criticalPressure_form
    # if cPresUnit_form[0]:
    criticalPressure_liq = meta_convert_P_T_FR_L('P', criticalPressure_form,
                                                    cPresUnit_form, 'bar (a)',
                                                    specificGravity * 1000)
    cPres_unit = 'bar (a)'
    # else:
    #     cPres_unit = cPresUnit_form[0]
    #     criticalPressure_liq = criticalPressure_form

    if fr_unit == 'm3/hr':
        length_unit_list_calculation = ['mm']
    elif fr_unit == 'gpm':
        length_unit_list_calculation = ['inch']
    else: 
        length_unit_list_calculation = ['mm']

    # 3. Length
    if iPipeUnit_form not in length_unit_list_calculation:
        inletPipeDia_liq = meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form,
                                                 'mm',
                                                 specificGravity * 1000) - 2 * thickness_pipe
        iPipe_unit = 'mm'
    else:
        iPipe_unit = iPipeUnit_form
        inletPipeDia_liq = inletPipeDia_form - 2 * thickness_pipe

    if oPipeUnit_form not in length_unit_list_calculation:
        outletPipeDia_liq = meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form,
                                                  'mm', specificGravity * 1000) - 2 * thickness_pipe
        oPipe_unit = 'mm'
    else:
        oPipe_unit = oPipeUnit_form
        outletPipeDia_liq = outletPipeDia_form - 2 * thickness_pipe

    if vSizeUnit_form not in length_unit_list_calculation:
        vSize_liq = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                          'mm', specificGravity * 1000)
        vSize_unit = 'mm'
    else:
        vSize_unit = vSizeUnit_form
        vSize_liq = valveSize_form

    print(f"dia of pipe: {outletPipeDia_liq}, {inletPipeDia_liq}")
    v_size_for_initial_cv = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                          'mm', specificGravity * 1000)

    service_conditions_sf = {'flowrate': flowrate_liq, 'flowrate_unit': fr_unit,
                             'iPres': inletPressure_liq, 'oPres': outletPressure_liq,
                             'iPresUnit': iPres_unit,
                             'oPresUnit': oPres_unit, 'temp': inletTemp_form,
                             'temp_unit': iTempUnit_form, 'sGravity': specificGravity,
                             'iPipeDia': inletPipeDia_liq,
                             'oPipeDia': outletPipeDia_liq,
                             'valveDia': vSize_liq, 'iPipeDiaUnit': iPipe_unit,
                             'oPipeDiaUnit': oPipe_unit, 'valveDiaUnit': vSize_unit,
                             'C': 0.075 * v_size_for_initial_cv * v_size_for_initial_cv, 'FR': 1, 'vPres': vaporPressure, 'Fl': xt_fl,
                             'Ff': 0.90,
                             'cPres': criticalPressure_liq,
                             'FD': fd, 'viscosity': viscosity}

    service_conditions_1 = service_conditions_sf
    N1_val = N1[(service_conditions_1['flowrate_unit'], str(service_conditions_1['iPresUnit']).split(' ')[0])]
    N2_val = N2[service_conditions_1['valveDiaUnit']]
    N4_val = N4[(service_conditions_1['flowrate_unit'], service_conditions_1['valveDiaUnit'])]

    result_1 = CV(service_conditions_1['flowrate'], service_conditions_1['C'],
                  service_conditions_1['valveDia'],
                  service_conditions_1['iPipeDia'],
                  service_conditions_1['oPipeDia'], N2_val, service_conditions_1['iPres'],
                  service_conditions_1['oPres'],
                  service_conditions_1['sGravity'], N1_val, service_conditions_1['FD'],
                  service_conditions_1['vPres'],
                  service_conditions_1['Fl'], service_conditions_1['cPres'], N4_val,
                  service_conditions_1['viscosity'], thickness_pipe)

    result = CV(service_conditions_1['flowrate'], result_1,
                service_conditions_1['valveDia'],
                service_conditions_1['iPipeDia'],
                service_conditions_1['oPipeDia'], N2_val, service_conditions_1['iPres'],
                service_conditions_1['oPres'],
                service_conditions_1['sGravity'], N1_val, service_conditions_1['FD'],
                service_conditions_1['vPres'],
                service_conditions_1['Fl'], service_conditions_1['cPres'], N4_val,
                service_conditions_1['viscosity'], thickness_pipe)

    ff_liq = FF(service_conditions_1['vPres'], service_conditions_1['cPres'])
    # if valveSize_form != inletPipeDia_form:
    #     FLP = flP(result, service_conditions_1['valveDia'], service_conditions_1['iPipeDia'], N2_value, service_conditions_1['Fl'])
    #     FP = fP(result, service_conditions_1['valveDia'], service_conditions_1['iPipeDia'], service_conditions_1['oPipeDia'], N2_value)
    #     # print(f"FP: {FP}")
    #     FL = FLP / FP
    # else:
    #     FL = service_conditions_1['Fl']
    chokedP = delPMax(service_conditions_1['Fl'], ff_liq, service_conditions_1['iPres'], service_conditions_1['vPres'])
    print("liq sizing function, delpMax")

    # noise and velocities
    # Liquid Noise - need flowrate in kg/s, valves in m, density in kg/m3, pressure in pa
    # convert form data in units of noise formulae
    valveDia_lnoise = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form, 'm', 1000)
    iPipeDia_lnoise = meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'm',
                                            1000)
    oPipeDia_lnoise = meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form, 'm',
                                            1000)
    seat_dia_lnoise = meta_convert_P_T_FR_L('L', seatDia, seatDiaUnit, 'm',
                                            1000)

    inletPipeDia_v = round(meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                                 1000))
    
    try:

        i_pipearea_element = i_pipearea_element
        thickness_pipe = float(i_pipearea_element.thickness)
    except:
        thickness_pipe = 1.24
# print(f"pipe dia: {inletPipeDia_v}, sch: {iSch}")

    iPipeSch_lnoise = meta_convert_P_T_FR_L('L', float(thickness_pipe),
                                            'mm', 'm', 1000)
    
    flowrate_lnoise = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'kg/hr',
                                            specificGravity * 1000) / 3600
    outletPressure_lnoise = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                                  'pa (a)', 1000)
    inletPressure_lnoise = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form,
                                                 'pa (a)', 1000)
    vPres_lnoise = meta_convert_P_T_FR_L('P', vaporPressure, vPresUnit_form, 'pa (a)', 1000)
    # print(f"3 press: {outletPressure_lnoise, inletPressure_lnoise, vPres_lnoise}")
    # service conditions for 4 inch vale with 8 as line size. CVs need to be changed
    sc_liq_sizing = {'valveDia': valveDia_lnoise, 'ratedCV': ratedCV, 'reqCV': result, 'FL': xt_fl,
                     'FD': fd,
                     'iPipeDia': iPipeDia_lnoise, 'iPipeUnit': 'm', 'oPipeDia': oPipeDia_lnoise,
                     'oPipeUnit': 'm',
                     'internalPipeDia': oPipeDia_lnoise,
                     'inPipeDiaUnit': 'm', 'pipeWallThickness': iPipeSch_lnoise, 'speedSoundPipe': sosPipe,
                     'speedSoundPipeUnit': 'm/s',
                     'densityPipe': densityPipe, 'densityPipeUnit': 'kg/m3', 'speedSoundAir': 343,
                     'densityAir': 1293,
                     'massFlowRate': flowrate_lnoise, 'massFlowRateUnit': 'kg/s',
                     'iPressure': inletPressure_lnoise,
                     'iPresUnit': 'pa',
                     'oPressure': outletPressure_lnoise,
                     'oPresUnit': 'pa', 'vPressure': vPres_lnoise, 'densityLiq': specificGravity * 1000,
                     'speedSoundLiq': 1400,
                     'rw': rw_noise,
                     'seatDia': seat_dia_lnoise,
                     'fi': 8000}

    sc_1 = sc_liq_sizing
    try:
        summation = Lpe1m(sc_1['fi'], sc_1['FD'], sc_1['reqCV'], sc_1['iPressure'], sc_1['oPressure'],
                        sc_1['vPressure'],
                        sc_1['densityLiq'], sc_1['speedSoundLiq'], sc_1['massFlowRate'], sc_1['rw'],
                        sc_1['FL'],
                        sc_1['seatDia'], sc_1['valveDia'], sc_1['densityPipe'], sc_1['pipeWallThickness'],
                        sc_1['speedSoundPipe'],
                        sc_1['densityAir'], sc_1['internalPipeDia'], sc_1['speedSoundAir'],
                        sc_1['speedSoundPipe'])
    except ZeroDivisionError:
        summation = 10
    except ValueError:
        summation = 10
    except TypeError:
        summation = 10
    # summation = 56

    # Power Level
    outletPressure_p = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                             'psia (a)', specificGravity * 1000)
    inletPressure_p = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form,
                                            'psia (a)', specificGravity * 1000)
    pLevel = power_level_liquid(inletPressure_p, outletPressure_p, specificGravity, result)

    # convert flowrate and dias for velocities
    flowrate_v = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'm3/hr',
                                       1000)
    inletPipeDia_v = round(meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                                 1000))
    outletPipeDia_v = round(meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form, 'inch',
                                                  1000))
    vSize_v = round(meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                          'inch', specificGravity * 1000))

    # convert pressure for tex, p in bar, l in inch
    inletPressure_v = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form, 'psia (a)',
                                            1000)
    outletPressure_v = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form, 'psia (a)',
                                             1000)

    v_det_element = valve_element
    db.session.commit()
    trim_type_element = db.session.query(trimType).filter_by(id=v_det_element.trimTypeId).first()
    trimtype = trim_type_element.name
    db.session.commit()
    t_caps = trimtype

    tEX = trimExitVelocity(inletPressure_v, outletPressure_v, specificGravity, t_caps, 'other')

    flow_character = getFlowCharacter(v_det_element.flowCharacter__.name)
    # new trim exit velocity
    # for port area, travel filter not implemented
    # tex new
    if float(travel) in [2, 3, 8]:
        travel = int(travel)
    else:
        travel = float(travel)

    if float(seatDia) in [1, 11, 2, 3, 4, 7, 8]:
        seatDia = int(seatDia)
    else:
        seatDia = float(seatDia)
    try:
        port_area_ = port_area_
    except:
        port_area_ = None
    print(f"port area table inputs: {vSize_v}, {seatDia}, {trimtype}, {flow_character}, {travel}")
    # if port_area_:
    #     port_area = float(port_area_.area)
    #     tex_ = tex_new(result, int(rated_cv_tex), port_area, flowrate_v / 3600, inletPressure_form, inletPressure_form,
    #                    1, 8314,
    #                    inletTemp_form, 'Liquid')
    # else:
    #     port_area = 1
    #     tex_ = None
    if port_area_:
        port_area = float(port_area_.area)
    else:
        port_area = 1
    # tex_ = tex_new(result, ratedCV, port_area, flowrate_v / 3600, inletPressure_form, inletPressure_form, 1, 8314,
    #                inletTemp_form, 'Liquid')
    tex_ = trimExitVelocityLiquid(inletPressure_v, outletPressure_v, trimtype, specificGravity)

    # ipipeSch_v = meta_convert_P_T_FR_L('L', float(iPipeSch_form), iPipeSchUnit_form,
    #                                    'inch',
    #                                    1000)
    # opipeSch_v = meta_convert_P_T_FR_L('L', float(oPipeSch_form), oPipeSchUnit_form,
    #                                    'inch',
    #                                    1000)
    # iVelocity, oVelocity, pVelocity = getVelocity(flowrate_v, inletPipeDia_v,
    #                                               outletPipeDia_v,
    #                                               vSize_v)
    # print(flowrate_v, (inletPipeDia_v - ipipeSch_v),
    #       (outletPipeDia_v - opipeSch_v),
    #       vSize_v)
    
    try:
        i_pipearea_element = i_pipearea_element
        area_in2 = float(i_pipearea_element.area)
        a_i = 0.00064516 * area_in2
        iVelocity = flowrate_v / (3600 * a_i)

        o_pipearea_element = i_pipearea_element
        print(f"oPipedia: {outletPipeDia_v}, sch: {oSch}")
        area_in22 = float(o_pipearea_element.area)
        a_o = 0.00064516 * area_in22
        oVelocity = flowrate_v / (3600 * a_o)
    except:
        a_i = 0.00064516 * 0.074
        iVelocity = flowrate_v / (3600 * a_i)
        a_o = 0.00064516 * 0.074
        oVelocity = flowrate_v / (3600 * a_o)
    valve_element_current = valve_element
    rating_current = valve_element_current.rating
    valvearea_element = valvearea_element
    if valvearea_element:
        v_area_in = float(valvearea_element.area)
        v_area = 0.00064516 * v_area_in
    else:
        v_area = 0.00064516 * 1
    pVelocity = flowrate_v / (3600 * v_area)

    data = {'cv': round(result, 3),
            'percent': open_percent,
            'spl': round(summation, 3),
            'iVelocity': iVelocity,
            'oVelocity': round(oVelocity, 3), 'pVelocity': round(pVelocity, 3), 'choked': round(chokedP, 3),
            'texVelocity': round(433.9764, 3)}

    units_string = f"{seatDia}+{seatDiaUnit}+{sosPipe}+{densityPipe}+{rw_noise}+{fl_unit_form}+{iPresUnit_form}+{oPresUnit_form}+{vPresUnit_form}+{cPresUnit_form}+{iPipeUnit_form}+{oPipeUnit_form}+{vSizeUnit_form}+{iPipeSchUnit_form}+{oPipeSchUnit_form}+{iTempUnit_form}+sg"

    # update valve size in item
    size_in_in = int(round(meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form, 'inch', 1000)))
    size_id = valveSize_form
    print(size_id)
    item_selected.size = size_id
    # load case data with item ID
    # get valvetype - kc requirements
    v_det_element = valve_element
    valve_type_ = v_det_element.style.name
    trim_type_element = db.session.query(trimType).filter_by(id=v_det_element.trimTypeId).first()
    trimtype = trim_type_element.name
    outletPressure_psia = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                                'psia (a)', 1000)
    inletPressure_psia = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form,
                                               'psia (a)', 1000)
    dp_kc = inletPressure_psia - outletPressure_psia
    # Kc = getKCValue(size_in_in, trimtype, dp_kc, valve_type_.lower(), xt_fl)
    Kc = getKc(size_in_in, trimtype, dp_kc, valve_type_, xt_fl)

    # get other req values - Ff, Kc, Fd, Flp, Reynolds Number
    Ff_liq = round(FF(service_conditions_1['vPres'], service_conditions_1['cPres']), 2)
    N2_fp = N2[vSizeUnit_form]
    Fd_liq = service_conditions_1['FD']
    FLP_liq = flP(result, valveSize_form, inletPipeDia_form, N2_fp,
                  service_conditions_1['Fl'])
    RE_number = reynoldsNumber(N4_val, service_conditions_1['FD'], service_conditions_1['flowrate'],
                               service_conditions_1['viscosity'], service_conditions_1['Fl'], N2_val,
                               service_conditions_1['iPipeDia'], N1_val, service_conditions_1['iPres'],
                               service_conditions_1['oPres'],
                               service_conditions_1['sGravity'])
    fp_liq = fP(result, valveSize_form, inletPipeDia_form,
                outletPipeDia_form, N2_fp)
    if valveSize_form != inletPipeDia_form:
        FL_ = (FLP_liq / fp_liq)
        print(f"FL is flp/fp: {FL_}")
    else:
        FL_ = service_conditions_1['Fl']
        print(f'fl is just fl: {FL_}')
    chokedP = delPMax(FL_, ff_liq, service_conditions_1['iPres'], service_conditions_1['vPres'])
    print(FL_, ff_liq, service_conditions_1['iPres'], service_conditions_1['vPres'], valveSize_form, inletPipeDia_form,
          FLP_liq, fp_liq)
    if chokedP == (service_conditions_1['iPres'] - service_conditions_1['oPres']):
        ff = 0.96
    else:
        ff = round(ff_liq, 3)

    vp_ar = meta_convert_P_T_FR_L('P', vaporPressure, vPres_unit, iPresUnit_form, 1000)
    application_ratio = (inletPressure_form - outletPressure_form) / (inletPressure_form - vp_ar)
    other_factors_string = f"{ff}+{Kc}+{Fd_liq}+{round(FLP_liq, 3)}+{RE_number}+{round(fp_liq, 2)}+{round(application_ratio, 3)}+{rated_cv_tex}"


    result_dict = {
        'flowrate': flowrate_form,
        'inletPressure':inletPressure_form,
        'outletPressure': outletPressure_form,
        'inletTemp': inletTemp_form,
        'specificGravity': specificGravity,
        'vaporPressure': vaporPressure,
        'kinematicViscosity': viscosity,
        'valveSize': valveSize_form,
        'fd': Fd_liq,
        'Ff': ff,
        'Fp': fp_liq,
        'Flp': FLP_liq,
        'ratedCv': ratedCV,
        'ar': round(application_ratio, 3),
        'kc': Kc,
        'reNumber': RE_number,
        'calculatedCv': round(result, 3),
        'openingPercentage': data['percent'],
        'spl': round(summation, 3),
        'pipeInVel': round(iVelocity, 3),
        'pipeOutVel': round(oVelocity, 3),
        'valveVel': round(pVelocity, 3),
        'chokedDrop': round(chokedP, 4),
        'fl': xt_fl,
        'tex': tex_,
        'powerLevel': pLevel,
        'seatDia': seatDia,
        'criticalPressure': criticalPressure_form,
        'inletPipeSize': inletPipeDia_form,
        'outletPipeSize': outletPipeDia_form,
        }

    output = result_dict

    return result_dict


def gasSizing(inletPressure_form, outletPressure_form, inletPipeDia_form, outletPipeDia_form, valveSize_form,
              specificGravity, flowrate_form, inletTemp_form, ratedCV, z_factor, vaporPressure, seatDia, seatDiaUnit,
              sosPipe, densityPipe, criticalPressure_form, viscosity, item_selected, fl_unit_form, iPresUnit_form,
              oPresUnit_form, vPresUnit_form, iPipeUnit_form, oPipeUnit_form, vSizeUnit_form, iSch,
              iPipeSchUnit_form, oSch, oPipeSchUnit_form, iTempUnit_form, xt_fl, sg_vale, sg_choice,
              open_percent, fd, travel, rated_cv_tex, fluidName, cv_table, i_pipearea_element, 
              valve_element, port_area_, trimtype, flow_character):
    # Unit Conversion
    # 1. Flowrate

    # 2. Pressure

    # logic to choose which formula to use - using units of flowrate and sg
    inletPipeDia_v = round(meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                                 1000))

    try:

        i_pipearea_element = i_pipearea_element
        thickness_pipe = float(i_pipearea_element.thickness)
    except:
        thickness_pipe = 1.24
    thickness_in = meta_convert_P_T_FR_L('L', thickness_pipe, 'mm', 'inch', 1000)
    fl_unit = fl_unit_form
    if fl_unit in ['m3/hr', 'scfh', 'gpm']:
        fl_bin = 1
    else:
        fl_bin = 2

    sg_unit = sg_choice
    if sg_unit == 'sg':
        sg_bin = 1
    else:
        sg_bin = 2

    def chooses_gas_fun(flunit, sgunit):
        eq_dict = {(1, 1): 1, (1, 2): 2, (2, 1): 3, (2, 2): 4}
        return eq_dict[(flunit, sgunit)]

    sg__ = chooses_gas_fun(fl_bin, sg_bin)

    if sg__ == 1:
        # to be converted to scfh, psi, R, in
        # 3. Pressure
        inletPressure = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form,
                                              'psia',
                                              1000)
        outletPressure = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                               'psia',
                                               1000)
        # 4. Length
        inletPipeDia = meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                             1000) - 2 * thickness_in
        outletPipeDia = meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form,
                                              'inch',
                                              1000) - 2 * thickness_in
        vSize = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                      'inch', specificGravity * 1000)
        # 1. Flowrate
        flowrate = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'scfh',
                                         1000)
        # 2. Temperature
        inletTemp = meta_convert_P_T_FR_L('T', inletTemp_form, iTempUnit_form, 'R',
                                          1000)
    elif sg__ == 2:
        # to be converted to m3/hr, kPa, C, in
        # 3. Pressure
        inletPressure = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form, 'kpa',
                                              1000)
        outletPressure = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                               'kpa',
                                               1000)
        # 4. Length
        inletPipeDia = meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                             1000) - 2 * thickness_in
        outletPipeDia = meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form,
                                              'inch',
                                              1000) - 2 * thickness_in
        vSize = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                      'inch', specificGravity * 1000)
        # 1. Flowrate
        flowrate = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'm3/hr',
                                         1000)
        # 2. Temperature
        inletTemp = meta_convert_P_T_FR_L('T', inletTemp_form, iTempUnit_form, 'K',
                                          1000)
    elif sg__ == 3:
        # to be converted to lbhr, psi, F, in
        # 3. Pressure
        inletPressure = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form,
                                              'psia',
                                              1000)
        outletPressure = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                               'psia',
                                               1000)
        # 4. Length
        inletPipeDia = meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                             1000) - 2 * thickness_in
        # print(iPipeUnit_form)
        outletPipeDia = meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form,
                                              'inch',
                                              1000) - 2 * thickness_in
        vSize = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                      'inch', specificGravity * 1000)
        # 1. Flowrate
        flowrate = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'lb/hr',
                                         1000)
        # 2. Temperature
        inletTemp = meta_convert_P_T_FR_L('T', inletTemp_form, iTempUnit_form, 'F',
                                          1000)
    else:
        # to be converted to kg/hr, bar, K, in
        # 3. Pressure
        inletPressure = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form, 'bar (a)',
                                              1000)
        outletPressure = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                               'bar (a)',
                                               1000)
        # 4. Length
        inletPipeDia = meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                             1000) - 2 * thickness_in
        outletPipeDia = meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form,
                                              'inch',
                                              1000) - 2 * thickness_in
        vSize = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                      'inch', specificGravity * 1000)
        # 1. Flowrate
        flowrate = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'kg/hr',
                                         1000)
        # 2. Temperature
        inletTemp = meta_convert_P_T_FR_L('T', inletTemp_form, iTempUnit_form, 'K',
                                          1000)

    print(f"dia of pipe: {outletPipeDia}, {inletPipeDia}")

    # python sizing function - gas

    inputDict_4 = {"inletPressure": inletPressure, "outletPressure": outletPressure,
                   "gamma": specificGravity,
                   "C": ratedCV,
                   "valveDia": vSize,
                   "inletDia": inletPipeDia,
                   "outletDia": outletPipeDia, "xT": float(xt_fl),
                   "compressibilityFactor": z_factor,
                   "flowRate": flowrate,
                   "temp": inletTemp, "sg": float(sg_vale), "sg_": sg__}

    print(inputDict_4)

    inputDict = inputDict_4
    N2_val = N2['inch']

    CV__ = Cv_gas(inletPressure=inputDict['inletPressure'], outletPressure=inputDict['outletPressure'],
                  gamma=inputDict['gamma'],
                  C=inputDict['C'], valveDia=inputDict['valveDia'], inletDia=inputDict['inletDia'],
                  outletDia=inputDict['outletDia'], xT=inputDict['xT'],
                  compressibilityFactor=inputDict['compressibilityFactor'],
                  flowRate=inputDict['flowRate'], temp=inputDict['temp'], sg=inputDict['sg'],
                  sg_=inputDict['sg_'], N2_value=N2_val)
    Cv__ = Cv_gas(inletPressure=inputDict['inletPressure'], outletPressure=inputDict['outletPressure'],
                  gamma=inputDict['gamma'],
                  C=CV__[0], valveDia=inputDict['valveDia'], inletDia=inputDict['inletDia'],
                  outletDia=inputDict['outletDia'], xT=inputDict['xT'],
                  compressibilityFactor=inputDict['compressibilityFactor'],
                  flowRate=inputDict['flowRate'], temp=inputDict['temp'], sg=inputDict['sg'],
                  sg_=inputDict['sg_'], N2_value=N2_val)
    Cv1 = Cv__[0]

    xChoked = xChoked_gas(gamma=inputDict['gamma'], C=inputDict['C'], valveDia=inputDict['valveDia'],
                          inletDia=inputDict['inletDia'], outletDia=inputDict['outletDia'],
                          xT=inputDict['xT'], N2_value=N2_val)

    # noise and velocities
    # Liquid Noise - need flowrate in kg/s, valves in m, density in kg/m3, pressure in pa
    inletPressure_gnoise = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form,
                                                 'pa (a)',
                                                 1000)
    outletPressure_gnoise = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                                  'pa (a)',
                                                  1000)
    # vaporPressure_gnoise = meta_convert_P_T_FR_L('P', vaporPressure, vPresUnit_form, 'pa',
    #                                              1000)
    flowrate_gnoise = conver_FR_noise(flowrate_form, fl_unit)
    inletPipeDia_gnoise = meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'm',
                                                specificGravity * 1000)
    outletPipeDia_gnoise = meta_convert_P_T_FR_L('L', outletPipeDia_form, iPipeUnit_form,
                                                 'm',
                                                 specificGravity * 1000)
    size_gnoise = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                        'm', specificGravity * 1000)
    seat_dia_gnoise = meta_convert_P_T_FR_L('L', seatDia, seatDiaUnit, 'm',
                                            1000)
    mw = float(sg_vale)
    if sg_unit == 'sg':
        mw = 28.96 * float(sg_vale)
    elif sg_unit == 'mw':
        mw = float(sg_vale)

    temp_gnoise = meta_convert_P_T_FR_L('T', inletTemp_form, iTempUnit_form, 'K', 1000)
    flp = fLP(Cv1, valveSize_form, inletPipeDia_form)
    fp = fP_gas(Cv1, valveSize_form, inletPipeDia_form, outletPipeDia_form, N2_val)
    sigmeta = sigmaEta_gas(valveSize_form, inletPipeDia_form, outletPipeDia_form)
    flowrate_gv = flowrate_form / 3600
    inlet_density = inletDensity(inletPressure_gnoise, mw, 8314, temp_gnoise)
    if sigmeta == 0:
        sigmeta = 0.86
    sc_initial_1 = {'valveSize': size_gnoise, 'valveOutletDiameter': outletPipeDia_gnoise,
                    'ratedCV': ratedCV,
                    'reqCV': 175,
                    'No': 6,
                    'FLP': flp,
                    'Iw': 0.181, 'valveSizeUnit': 'm', 'IwUnit': 'm', 'A': 0.00137,
                    'xT': float(xt_fl),
                    'iPipeSize': inletPipeDia_gnoise,
                    'oPipeSize': outletPipeDia_gnoise,
                    'tS': 0.008, 'Di': outletPipeDia_gnoise, 'SpeedOfSoundinPipe_Cs': sosPipe,
                    'DensityPipe_Ps': densityPipe,
                    'densityUnit': 'kg/m3',
                    'SpeedOfSoundInAir_Co': 343, 'densityAir_Po': 1.293, 'atmPressure_pa': 101325,
                    'atmPres': 'pa',
                    'stdAtmPres_ps': 101325, 'stdAtmPres': 'pa', 'sigmaEta': sigmeta, 'etaI': 1.2, 'Fp': fp,
                    'massFlowrate': flowrate_gnoise, 'massFlowrateUnit': 'kg/s',
                    'iPres': inletPressure_gnoise, 'iPresUnit': 'pa',
                    'oPres': outletPressure_gnoise, 'oPresUnit': 'pa', 'inletDensity': 5.3,
                    'iAbsTemp': temp_gnoise,
                    'iAbsTempUnit': 'K',
                    'specificHeatRatio_gamma': specificGravity, 'molecularMass': mw, 'mMassUnit': 'kg/kmol',
                    'internalPipeDia': inletPipeDia_gnoise,
                    'aEta': -3.8, 'stp': 0.2, 'R': 8314, 'RUnit': "J/kmol x K", 'fs': 1}

    sc_initial_2 = {'valveSize': size_gnoise, 'valveOutletDiameter': outletPipeDia_gnoise,
                    'ratedCV': ratedCV,
                    'reqCV': Cv1, 'No': 1,
                    'FLP': flp,
                    'Iw': 0.181, 'valveSizeUnit': 'm', 'IwUnit': 'm', 'A': 0.00137,
                    'xT': float(xt_fl),
                    'iPipeSize': inletPipeDia_gnoise,
                    'oPipeSize': outletPipeDia_gnoise,
                    'tS': 0.008, 'Di': inletPipeDia_gnoise, 'SpeedOfSoundinPipe_Cs': sosPipe,
                    'DensityPipe_Ps': densityPipe,
                    'densityUnit': 'kg/m3',
                    'SpeedOfSoundInAir_Co': 343, 'densityAir_Po': 1.293, 'atmPressure_pa': 101325,
                    'atmPres': 'pa',
                    'stdAtmPres_ps': 101325, 'stdAtmPres': 'pa', 'sigmaEta': sigmeta, 'etaI': 1.2, 'Fp': 0.98,
                    'massFlowrate': flowrate_gv, 'massFlowrateUnit': 'kg/s', 'iPres': inletPressure_gnoise,
                    'iPresUnit': 'pa',
                    'oPres': outletPressure_gnoise, 'oPresUnit': 'pa', 'inletDensity': inlet_density,
                    'iAbsTemp': temp_gnoise,
                    'iAbsTempUnit': 'K',
                    'specificHeatRatio_gamma': specificGravity, 'molecularMass': mw,
                    'mMassUnit': 'kg/kmol',
                    'internalPipeDia': inletPipeDia_gnoise,
                    'aEta': -3.8, 'stp': 0.2, 'R': 8314, 'RUnit': "J/kmol x K", 'fs': 1}
    # print(sc_initial)
    sc_initial = sc_initial_2

    try:
        summation1 = lpae_1m(sc_initial['specificHeatRatio_gamma'], sc_initial['iPres'], sc_initial['oPres'],
                            sc_initial['FLP'],
                            sc_initial['Fp'],
                            sc_initial['inletDensity'], sc_initial['massFlowrate'], sc_initial['aEta'],
                            sc_initial['R'],
                            sc_initial['iAbsTemp'],
                            sc_initial['molecularMass'], sc_initial['oPipeSize'],
                            sc_initial['internalPipeDia'], sc_initial['stp'],
                            sc_initial['No'],
                            sc_initial['A'], sc_initial['Iw'], sc_initial['reqCV'],
                            sc_initial['SpeedOfSoundinPipe_Cs'],
                            sc_initial['SpeedOfSoundInAir_Co'],
                            sc_initial['valveSize'], sc_initial['tS'], sc_initial['fs'],
                            sc_initial['atmPressure_pa'],
                            sc_initial['stdAtmPres_ps'], sc_initial['DensityPipe_Ps'], -3.002)
    except:
        summation1 = 80
    print(f'gas summation noise: {summation1}')
    # summation1 = 97

    # convert flowrate and dias for velocities
    flowrate_v = round(meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'm3/hr',
                                             mw / 22.4))
    inletPipeDia_v = round(meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                                 1000))
    outletPipeDia_v = round(meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form, 'inch',
                                                  1000))

    size_v = round(meta_convert_P_T_FR_L('L', valveSize_form, 'inch',
                                         'inch', specificGravity * 1000))
    print(f"vsize_form: {valveSize_form}, vsize_unit: {vSizeUnit_form}")

    # get gas velocities
    inletPressure_gv = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form, 'pa (a)',
                                             1000)
    outletPressure_gv = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form, 'pa (a)',
                                              1000)
    flowrate_gv = flowrate_form / 3600
    print(f'flowrate_gv: {flowrate_gv}')
    inletPipeDia_gnoise = meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'm',
                                                specificGravity * 1000)
    outletPipeDia_gnoise = meta_convert_P_T_FR_L('L', outletPipeDia_form, iPipeUnit_form,
                                                 'm',
                                                 specificGravity * 1000)
    size_gnoise = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                        'm', specificGravity * 1000)
    temp_gnoise = meta_convert_P_T_FR_L('T', inletTemp_form, iTempUnit_form, 'K', 1000)

    gas_vels = getGasVelocities(sc_initial['specificHeatRatio_gamma'], inletPressure_gv, outletPressure_gv, 8314,
                                temp_gnoise, sc_initial['molecularMass'], flowrate_gv, size_gnoise,
                                inletPipeDia_gnoise, outletPipeDia_gnoise)

    # Power Level
    # getting fr in lb/s
    flowrate_p = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'kg/hr',
                                       specificGravity * 1000)
    inletPressure_p = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form, 'pa (a)',
                                            1000)
    outletPressure_p = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                             'pa (a)',
                                             1000)
    # pLevel = power_level_gas(specificGravity, inletPressure_p, outletPressure_p, flowrate_p, gas_vels[9])
    pLevel = getPowerLevelGas(sc_initial['iPres'], sc_initial['oPres'], sc_initial['specificHeatRatio_gamma'], 
                              sc_initial['FLP'], sc_initial['Fp'],
                            sc_initial['inletDensity'], sc_initial['massFlowrate'])
    print(sc_initial['specificHeatRatio_gamma'], inletPressure_gv, outletPressure_gv, 8314,
          temp_gnoise, sc_initial['molecularMass'], flowrate_gv, size_gnoise,
          inletPipeDia_gnoise, outletPipeDia_gnoise)
    print(f"gas velocities: {gas_vels}")

    # endof get gas

    # convert pressure for tex, p in bar, l in in
    inletPressure_v = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form, 'pa (a)',
                                            1000)
    outletPressure_v = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form, 'pa (a)',
                                             1000)
    # print(f"Outlet Pressure V{outletPressure_v}")

    # get tex pressure in psi
    inletPressure_tex = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form, 'psia (a)',
                                              1000)
    outletPressure_tex = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form, 'psia (a)',
                                               1000)

    tEX = trimExitVelocityGas(inletPressure_tex, outletPressure_tex) / 3.281
    print(f"tex: {tEX}, {inletPressure_tex}, {outletPressure_tex}, {inletPressure_tex - outletPressure_tex}")
    # print(summation1)
    iVelocity = gas_vels[6]
    oVelocity = gas_vels[7]
    pVelocity = gas_vels[8]

    data = {'cv': round(Cv1, 3),
            'percent': open_percent,
            'spl': round(summation1, 3),
            'iVelocity': round(iVelocity, 3),
            'oVelocity': round(oVelocity, 3), 'pVelocity': round(pVelocity, 3), 'choked': round(xChoked, 4),
            'texVelocity': round(tEX, 3)}

    units_string = f"{seatDia}+{seatDiaUnit}+{sosPipe}+{densityPipe}+{z_factor}+{fl_unit_form}+{iPresUnit_form}+{oPresUnit_form}+{oPresUnit_form}+{oPresUnit_form}+{iPipeUnit_form}+{oPipeUnit_form}+{vSizeUnit_form}+{iPipeSchUnit_form}+{oPipeSchUnit_form}+{iTempUnit_form}+{sg_choice}"
    # change valve in item
    size_in_in = int(round(meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form, 'inch', 1000)))
    size_id = valveSize_form
    print(size_id)
    item_selected.size = size_id
    # load case data with item ID
    # get valvetype - kc requirements
    v_det_element = valve_element
    valve_type_ = v_det_element.style.name
    trimtype = trimtype
    outletPressure_psia = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                                'psia (a)', 1000)
    inletPressure_psia = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form,
                                               'psia (a)', 1000)
    dp_kc = inletPressure_psia - outletPressure_psia
    # Kc = getKCValue(size_in_in, trimtype, dp_kc, valve_type_.lower(), xt_fl)
    Kc = getKc(size_in_in, trimtype, dp_kc, valve_type_, xt_fl)

    # get other req values - Ff, Kc, Fd, Flp, Reynolds Number#####
    Ff_gas = 0.96
    Fd_gas = fd
    xtp = xTP_gas(inputDict['xT'], inputDict['C'], inputDict['valveDia'], inputDict['inletDia'], inputDict['outletDia'],
                  N2_val)
    N1_val = 0.865
    N4_val = 76000
    inletPressure_re = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form, 'bar (a)',
                                             1000)
    outletPressure_re = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form, 'bar (a)',
                                              1000)
    inletPipeDia_re = round(meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'mm',
                                                  1000))
    flowrate_re = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'm3/hr',
                                        mw / 22.4)
    RE_number = reynoldsNumber(N4_val, Fd_gas, flowrate_re,
                               1, 0.9, N2_val,
                               inletPipeDia_re, N1_val, inletPressure_re,
                               outletPressure_re,
                               mw / 22400)

    fpgas = fP(inputDict['C'], inputDict['valveDia'], inputDict['inletDia'], inputDict['outletDia'], N2_val)
    if data['choked'] == (inputDict['inletPressure'] - inputDict['outletPressure']):
        ff = 0.96
    else:
        ff = round(Ff_gas, 3)
    mac_sonic_list = [gas_vels[0], gas_vels[1], gas_vels[2],
                      gas_vels[3], gas_vels[4], gas_vels[5], gas_vels[9]]
    other_factors_string = f"{Ff_gas}+{Kc}+{Fd_gas}+{xtp}+{RE_number}+{fpgas}"

    vp_ar = meta_convert_P_T_FR_L('P', vaporPressure, iPresUnit_form, iPresUnit_form, 1000)
    application_ratio = (inletPressure_form - outletPressure_form) / (inletPressure_form - vp_ar)
    other_factors_string = f"{Cv__[1]}+{Cv__[2]}+{Cv__[3]}+{Cv__[4]}+{Cv__[5]}+{Cv__[6]}+{Cv__[7]}+{Fd_gas}+{RE_number}+{Kc}+{mac_sonic_list[0]}+{mac_sonic_list[1]}+{mac_sonic_list[2]}+{mac_sonic_list[3]}+{mac_sonic_list[4]}+{mac_sonic_list[5]}+{mac_sonic_list[6]}+{round(application_ratio, 3)}+{ratedCV}"

    # tex new
    # flow_character_element = db.session.query(flowCharacter).filter_by(id=v_det_element.flowCharacter__.id).first()
    flow_character = getFlowCharacter(flow_character)
        # new trim exit velocity
        # for port area, travel filter not implemented

    if float(travel) in [2, 3, 8]:
        travel = int(travel)
    else:
        travel = float(travel)

    if float(seatDia) in [1, 11, 2, 3, 4, 7, 8]:
        seatDia = int(seatDia)
    else:
        seatDia = float(seatDia)
    try:
        port_area_ = port_area_
    except:
        port_area_ = None
    print(f'port area inputs: {size_in_in}, {seatDia}, {trimtype}, {flow_character}, {travel}')

    if port_area_:
        port_area = float(port_area_.area)
        tex_ = tex_new(Cv1, int(rated_cv_tex), port_area, flowrate_re / 3600, inletPressure_v, outletPressure_v, mw,
                       8314, temp_gnoise, 'Gas')
    else:
        port_area = 1
        tex_ = None

    result_dict = {
        'fk': Cv__[2],
        'y': Cv__[4],
        'xt': float(xt_fl),
        'xtp': Cv__[6],
        'fd': Fd_gas,
        'Fp': Cv__[7],
        'ratedCv': ratedCV,
        'ar': round(application_ratio, 3),
        'kc': Kc,
        'reNumber': RE_number,
        'calculatedCv': round(Cv1, 3),
        'openingPercentage': data['percent'],
        'spl': data['spl'],
        'pipeInVel': data['iVelocity'],
        'pipeOutVel': data['oVelocity'],
        'valveVel': data['pVelocity'],
        'chokedDrop': round(data['choked'] * inletPressure_form, 3),
        'fl': xt_fl,
        'tex': tex_,
        'powerLevel': pLevel,
        'seatDia': seatDia,
        'criticalPressure': criticalPressure_form,
        'inletPipeSize': inletPipeDia_form,
        'outletPipeSize': outletPipeDia_form,
        'machNoUp': mac_sonic_list[0],
        'machNoDown': mac_sonic_list[1],
        'machNoVel': mac_sonic_list[2],
        'sonicVelUp': mac_sonic_list[3],
        'sonicVelDown': mac_sonic_list[4],
        'sonicVelValve': mac_sonic_list[5],
        'outletDensity': mac_sonic_list[6],
        'x_delp': (inletPressure_form-outletPressure_form)/inletPressure_form,
        'outletPipeSize': outletPipeDia_form,
        'criticalPressure': round(criticalPressure_form, 3),
        'inletPipeSize': inletPipeDia_form,
        'molecularWeight': float(sg_vale),
        'kinematicViscosity': viscosity,
        'vaporPressure': vaporPressure,
        'specificGravity': specificGravity,
        'inletTemp': inletTemp_form,
        'outletPressure': outletPressure_form,
        'inletPressure':inletPressure_form,
        'flowrate':flowrate_form,
        }

    return result_dict


def getCVresult(fl_unit_form, specificGravity, iPresUnit_form, inletPressure_form, flowrate_form, outletPressure_form,
                oPresUnit_form,
                vPresUnit_form, vaporPressure, cPresUnit_form, criticalPressure_form, inletPipeDia_form, iPipeUnit_form,
                outletPipeDia_form, oPipeUnit_form, valveSize_form, vSizeUnit_form, inletTemp_form, ratedCV, xt_fl, fd,
                viscosity, iTempUnit_form):
    # 1. flowrate
    if fl_unit_form:
        flowrate_liq = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form,
                                             'm3/hr',
                                             specificGravity * 1000)
        fr_unit = 'm3/hr'
    else:
        fr_unit = fl_unit_form
        flowrate_liq = flowrate_form

    # 2. Pressure
    # A. inletPressure
    # print('GETCVRESULT')
    # iPresUnit_form = iPresUnit_form.split(' ')    

    # if iPresUnit_form[1] == '(g)':
    #     inletPressure_form_new = meta_convert_g_to_a(inletPressure_form,iPresUnit_form[0])
    #     print(f'Intermediates {inletPressure_form_new}')
    # else:
    #     inletPressure_form_new = inletPressure_form

    # if iPresUnit_form[0]:
    inletPressure_liq = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form,
                                                  'bar (a)', specificGravity * 1000)
    iPres_unit = 'bar (a)'
    # else:
    #     iPres_unit = iPresUnit_form[0]
    #     inletPressure_liq = inletPressure_form

    # B. outletPressure
    # oPresUnit_form = oPresUnit_form.split(' ')

    # if oPresUnit_form[1] == '(g)':
    #     outletPressure_form_new = meta_convert_g_to_a(outletPressure_form,oPresUnit_form[0])
    #     print(f'Intermediates {outletPressure_form_new}')
    # else:
    #     outletPressure_form_new = outletPressure_form

    # if oPresUnit_form:
    outletPressure_liq = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                                   'bar (a)', specificGravity * 1000)
    oPres_unit = 'bar (a)'
    # else:
    #     oPres_unit = oPresUnit_form[0]
    #     outletPressure_liq = outletPressure_form

    # C. vaporPressure
    # vPresUnit_form = vPresUnit_form.split(' ')
    # if vPresUnit_form[1] == '(g)':
    #     vaporPressure_form_new = meta_convert_g_to_a(vaporPressure,vPresUnit_form[0])
    #     print(f'Intermediates {vaporPressure_form_new}')
    # else:
    #     vaporPressure_form_new = vaporPressure

    # if vPresUnit_form:
    vaporPressure = meta_convert_P_T_FR_L('P', vaporPressure, vPresUnit_form, 'bar (a)',
                                            specificGravity * 1000)
    vPres_unit = 'bar (a)'
    # else:
    #     vPres_unit = vPresUnit_form[0]

    # D. Critical Pressure
    # cPresUnit_form = cPresUnit_form.split(' ')

    # if cPresUnit_form[1] == '(g)':
    #     criticalPressure_form_new = meta_convert_g_to_a(criticalPressure_form,cPresUnit_form[0])
    #     print(f'Intermediates {criticalPressure_form_new}')
    # else:
    #     criticalPressure_form_new = criticalPressure_form
    
    # if cPresUnit_form[0]:
    criticalPressure_liq = meta_convert_P_T_FR_L('P', criticalPressure_form,
                                                    cPresUnit_form, 'bar (a)',
                                                    specificGravity * 1000)
    cPres_unit = 'bar (a)'
    # else:
    #     cPres_unit = cPresUnit_form[0]
    #     criticalPressure_liq = criticalPressure_form

    # 3. Length
    if fr_unit == 'm3/hr':
        length_unit_list_calculation = ['mm']
    elif fr_unit == 'gpm':
        length_unit_list_calculation = ['inch']
    else: 
        length_unit_list_calculation = ['mm']

    if iPipeUnit_form not in length_unit_list_calculation:
        inletPipeDia_liq = meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form,
                                                 'mm',
                                                 specificGravity * 1000)
        iPipe_unit = 'mm'
    else:
        iPipe_unit = iPipeUnit_form
        inletPipeDia_liq = inletPipeDia_form

    if oPipeUnit_form not in length_unit_list_calculation:
        outletPipeDia_liq = meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form,
                                                  'mm', specificGravity * 1000)
        oPipe_unit = 'mm'
    else:
        oPipe_unit = oPipeUnit_form
        outletPipeDia_liq = outletPipeDia_form

    if vSizeUnit_form not in length_unit_list_calculation:
        vSize_liq = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                          'mm', specificGravity * 1000)
        vSize_unit = 'mm'
    else:
        vSize_unit = vSizeUnit_form
        vSize_liq = valveSize_form

    v_size_for_initial_cv = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                          'mm', specificGravity * 1000)

    service_conditions_sf = {'flowrate': flowrate_liq, 'flowrate_unit': fr_unit,
                             'iPres': inletPressure_liq, 'oPres': outletPressure_liq,
                             'iPresUnit': iPres_unit,
                             'oPresUnit': oPres_unit, 'temp': inletTemp_form,
                             'temp_unit': iTempUnit_form, 'sGravity': specificGravity,
                             'iPipeDia': inletPipeDia_liq,
                             'oPipeDia': outletPipeDia_liq,
                             'valveDia': vSize_liq, 'iPipeDiaUnit': iPipe_unit,
                             'oPipeDiaUnit': oPipe_unit, 'valveDiaUnit': vSize_unit,
                             'C': 0.075 * v_size_for_initial_cv * v_size_for_initial_cv, 'FR': 1, 'vPres': vaporPressure, 'Fl': xt_fl,
                             'Ff': 0.90,
                             'cPres': criticalPressure_liq,
                             'FD': fd, 'viscosity': viscosity}

    service_conditions_1 = service_conditions_sf
    N1_val = N1[(service_conditions_1['flowrate_unit'], str(service_conditions_1['iPresUnit']).split(' ')[0])]
    N2_val = N2[service_conditions_1['valveDiaUnit']]
    N4_val = N4[(service_conditions_1['flowrate_unit'], service_conditions_1['valveDiaUnit'])]

    result_1 = CV(service_conditions_1['flowrate'], service_conditions_1['C'],
                  service_conditions_1['valveDia'],
                  service_conditions_1['iPipeDia'],
                  service_conditions_1['oPipeDia'], N2_val, service_conditions_1['iPres'],
                  service_conditions_1['oPres'],
                  service_conditions_1['sGravity'], N1_val, service_conditions_1['FD'],
                  service_conditions_1['vPres'],
                  service_conditions_1['Fl'], service_conditions_1['cPres'], N4_val,
                  service_conditions_1['viscosity'], 0)

    result = CV(service_conditions_1['flowrate'], result_1,
                service_conditions_1['valveDia'],
                service_conditions_1['iPipeDia'],
                service_conditions_1['oPipeDia'], N2_val, service_conditions_1['iPres'],
                service_conditions_1['oPres'],
                service_conditions_1['sGravity'], N1_val, service_conditions_1['FD'],
                service_conditions_1['vPres'],
                service_conditions_1['Fl'], service_conditions_1['cPres'], N4_val,
                service_conditions_1['viscosity'], 0)

    return result


def getCVGas(fl_unit_form, specificGravity, sg_choice, inletPressure_form, iPresUnit_form, outletPressure_form,
             oPresUnit_form, valveSize_form, vSizeUnit_form,
             flowrate_form, inletTemp_form, iTempUnit_form, ratedCV, inletPipeDia_form, iPipeUnit_form,
             outletPipeDia_form, oPipeUnit_form, xt_fl, z_factor,
             sg_vale):
    # print(f'CVGASSSSSSVV {''.join(str(iPresUnit_form.split('  ')[0]))}')
    fl_unit = fl_unit_form
    if fl_unit in ['m3/hr', 'scfh', 'gpm']:
        fl_bin = 1
    else:
        fl_bin = 2

    sg_unit = sg_choice
    if sg_unit == 'sg':
        sg_bin = 1
    else:
        sg_bin = 2

    def chooses_gas_fun(flunit, sgunit):
        eq_dict = {(1, 1): 1, (1, 2): 2, (2, 1): 3, (2, 2): 4}
        return eq_dict[(flunit, sgunit)]

    sg__ = chooses_gas_fun(fl_bin, sg_bin)
    print(f'chosen function id is {sg__}')

    if sg__ == 1:
        # to be converted to scfh, psi, R, in
        # 3. Pressure
        inletPressure = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form,
                                              'psia',
                                              1000)
        outletPressure = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                               'psia',
                                               1000)
        # 4. Length
        inletPipeDia = meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                             1000)
        outletPipeDia = meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form,
                                              'inch',
                                              1000)
        vSize = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                      'inch', specificGravity * 1000)
        # 1. Flowrate
        flowrate = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'scfh',
                                         1000)
        # 2. Temperature
        inletTemp = meta_convert_P_T_FR_L('T', inletTemp_form, iTempUnit_form, 'R',
                                          1000)
    elif sg__ == 2:
        # to be converted to m3/hr, kPa, C, in
        # 3. Pressure
        inletPressure = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form, 'kpa',
                                              1000)
        outletPressure = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                               'kpa',
                                               1000)
        # 4. Length
        inletPipeDia = meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                             1000)
        outletPipeDia = meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form,
                                              'inch',
                                              1000)
        vSize = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                      'inch', specificGravity * 1000)
        # 1. Flowrate
        flowrate = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'm3/hr',
                                         1000)
        # 2. Temperature
        inletTemp = meta_convert_P_T_FR_L('T', inletTemp_form, iTempUnit_form, 'C',
                                          1000)
    elif sg__ == 3:
        # to be converted to lbhr, psi, F, in
        # 3. Pressure
        inletPressure = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form,
                                              'psia',
                                              1000)
        outletPressure = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                               'psia',
                                               1000)
        # 4. Length
        inletPipeDia = meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                             1000)
        # print(iPipeUnit_form)
        outletPipeDia = meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form,
                                              'inch',
                                              1000)
        vSize = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                      'inch', specificGravity * 1000)
        # 1. Flowrate
        flowrate = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'lb/hr',
                                         1000)
        # 2. Temperature
        inletTemp = meta_convert_P_T_FR_L('T', inletTemp_form, iTempUnit_form, 'F',
                                          1000)
    else:
        # to be converted to kg/hr, bar, K, in
        # 3. Pressure
        print(f'PRESUSREE {iPresUnit_form}')
        inletPressure = meta_convert_P_T_FR_L('P', inletPressure_form, iPresUnit_form, 'bar (a)',
                                              1000)
        outletPressure = meta_convert_P_T_FR_L('P', outletPressure_form, oPresUnit_form,
                                               'bar (a)',
                                               1000)
        # 4. Length
        inletPipeDia = meta_convert_P_T_FR_L('L', inletPipeDia_form, iPipeUnit_form, 'inch',
                                             1000)
        outletPipeDia = meta_convert_P_T_FR_L('L', outletPipeDia_form, oPipeUnit_form,
                                              'inch',
                                              1000)
        vSize = meta_convert_P_T_FR_L('L', valveSize_form, vSizeUnit_form,
                                      'inch', specificGravity * 1000)
        # 1. Flowrate
        flowrate = meta_convert_P_T_FR_L('FR', flowrate_form, fl_unit_form, 'kg/hr',
                                         1000)
        # 2. Temperature
        inletTemp = meta_convert_P_T_FR_L('T', inletTemp_form, iTempUnit_form, 'K',
                                          1000)

    # python sizing function - gas

    inputDict_4 = {"inletPressure": inletPressure, "outletPressure": outletPressure,
                   "gamma": specificGravity,
                   "C": ratedCV,
                   "valveDia": vSize,
                   "inletDia": inletPipeDia,
                   "outletDia": outletPipeDia, "xT": float(xt_fl),
                   "compressibilityFactor": z_factor,
                   "flowRate": flowrate,
                   "temp": inletTemp, "sg": float(sg_vale), "sg_": sg__}

    # print(inputDict_4)

    inputDict = inputDict_4
    N2_val = N2['inch']

    Cv__ = Cv_gas(inletPressure=inputDict['inletPressure'], outletPressure=inputDict['outletPressure'],
                  gamma=inputDict['gamma'],
                  C=inputDict['C'], valveDia=inputDict['valveDia'], inletDia=inputDict['inletDia'],
                  outletDia=inputDict['outletDia'], xT=inputDict['xT'],
                  compressibilityFactor=inputDict['compressibilityFactor'],
                  flowRate=inputDict['flowRate'], temp=inputDict['temp'], sg=inputDict['sg'],
                  sg_=inputDict['sg_'], N2_value=N2_val)
    Cv_gas_final = Cv__[0]
    return Cv_gas_final

@app.route('/getseatload')
def getseatload():
    itemId = request.args.get('itemId')
    seatDia = request.args.get('seatDia')
    valveElement = db.session.query(valveDetailsMaster).filter_by(itemId=itemId).first()
    trim = getDBElementWithId(trimType,valveElement.trimTypeId)   
    leakage = getDBElementWithId(seatLeakageClass,valveElement.seatLeakageClassId) 
    seatload = db.session.query(seatLoadForce)\
        .filter_by(trimType_=trim,leakage=leakage)\
        .order_by(func.abs(seatLoadForce.seatBore - float(seatDia)))\
        .first()
    value = seatload.value
    print(f'getseatload {seatDia},{valveElement.trimTypeId},{valveElement.seatLeakageClassId},{seatload},{value}')
    return{
        'value' : value 
    }

@app.route('/getpackingfriction')
def getpackingfriction():
    stemDia_id = request.args.get('stemDia')
    stemDia_element = getDBElementWithId(stemSize,stemDia_id)
    print(f'packingB4 {stemDia_element.stemDia}')
    decimal_stemdia = Decimal(float(Fraction(stemDia_element.stemDia)))
    
    itemId = request.args.get('itemId')
    valveElement = db.session.query(valveDetailsMaster).filter_by(itemId=itemId).first()
    rating_ = getDBElementWithId(ratingMaster,valveElement.ratingId)
    packing_ = getDBElementWithId(packing,valveElement.packingId)
    packingFrictionData = db.session.query(packingFriction).filter_by(stemDia=decimal_stemdia,rating=rating_,packing_=packing_).first()
    print(f'packingAF {decimal_stemdia},{rating_},{packing_}')
    value = packingFrictionData.value
    print(f'getpacking {packingFrictionData}')
    return {
        'value' : value
    }


@app.route('/valve-sizing/proj-<proj_id>/item-<item_id>', methods=['GET', 'POST'])
def valveSizing(proj_id, item_id):
    metadata_ = metadata()
    item_selected = getDBElementWithId(itemMaster, item_id)
    itemCases_1 = db.session.query(caseMaster).filter_by(item=item_selected).order_by(caseMaster.id).all()
    valve_element = db.session.query(valveDetailsMaster).filter_by(item=item_selected).first()
    try:
        f_state = valve_element.state.name
        valve_style = getValveType(valve_element.style.name)
        if valve_style == 'globe':
            constants = {'xt': 0.65, 'fl': 0.9}
        else:
            constants = {'xt': 0.2, 'fl': 0.55}
    except:
        constants = {'xt': 0.65, 'fl': 0.9}
    print(len(itemCases_1))
    if request.method =='POST':
        valve_style = getValveType(valve_element.style.name)
        f_state = valve_element.state.name
        data = request.form.to_dict(flat=False)
        a = jsonify(data).json
        print(f'JSONIFYA {a}')
        
        fluidOption = a['fluidOption'][0]
        pipeData = a['pipeData'][0]
        fluid_element = getDBElementWithId(fluidProperties, a['fluid_name'][0])
        print(f"Fluid Name: {fluid_element.fluidName}")
        standard_custom_dict = {'Standard': True, 'Custom': False}
        item_selected.standardStatus = standard_custom_dict[fluidOption]
        item_selected.pipeDataStatus = standard_custom_dict[pipeData]
        db.session.commit()
        
        # RW Noise
        if valve_style == 'globe':
            rw_noise = 0.25
        else:
            rw_noise = 0.5
        
        if a['inpipe_unit'][0] == "mm":
            i_pipearea_element = db.session.query(pipeArea)\
                .filter_by(schedule='std')\
                .order_by(func.abs(pipeArea.nominalDia - a['inletPipeSize'][0]))\
                .first()

        elif a['inpipe_unit'][0] == "inch":
                i_pipearea_element = db.session.query(pipeArea)\
                .filter_by(schedule='std')\
                .filter_by(nominalPipeSize=float(a['inletPipeSize'][0]))\
                .first()
        # print(f'PIPEELEMENT {i_pipearea_element},{a['inpipe_unit'][0]},{a['inletPipeSize'][0]}')

        port_area_ = db.session.query(portArea).filter_by(v_size=a['vSize'][0], trim_type="contour",
                                        flow_char="equal").first()
        valvearea_element = db.session.query(valveArea).filter_by(rating=valve_element.rating.name[5:],
                                                nominalPipeSize=a['vSize'][0]).first()
        # print(f'UNIT {a['inletPipeSize'][0]}')
        for i in itemCases_1:
            print('deleteing casees')
            db.session.delete(i)
            db.session.commit()

        if f_state == 'Liquid':
                len_cases_input = len(a['inletPressure'])
                
                try:
                    for k in range(len_cases_input):
                        try:
                            sch_element = db.session.query(pipeArea).filter_by(schedule=a['iSch'][0], nominalPipeSize=float(a['inletPipeSize'][0])).first()
                            output = getOutputs(a['flowrate'][k], a['flowrate_unit'][0], a['inletPressure'][k],
                                                a['inpres_unit'][0],
                                                a['outletPressure'][k], a['outpres_unit'][0],
                                                a['inletTemp'][k], a['temp_unit'][0], a['vaporPressure'][k], 
                                                a['vaporpres_unit'][0],
                                                a['specificGravity'][k], a['kinematicViscosity'][k],
                                                a['fl'][k], a['criticalPressure'][0], a['criticalpres_unit'][0], a['inletPipeSize'][0],
                                                a['inpipe_unit'][0], a['iSch'][0],
                                                a['outletPipeSize'][0], a['outpipe_unit'][0], a['oSch'][0], 7800,
                                                5000, a['vSize'][0],
                                                a['valvesize_unit'][0], a['vSize'][0], a['valvesize_unit'][0], a['ratedCV'][0],
                                                rw_noise, item_selected, fluid_element.fluidName, valve_element, i_pipearea_element, port_area_,valvearea_element)
                            

                            new_case = caseMaster(flowrate=output['flowrate'], inletPressure=output['inletPressure'],
                                                    outletPressure=output['outletPressure'], fluid=fluid_element,
                                                    inletTemp=output['inletTemp'], specificGravity=output['specificGravity'],
                                                    vaporPressure=output['vaporPressure'], kinematicViscosity=output['kinematicViscosity'],
                                                    calculatedCv=output['calculatedCv'], openingPercentage=output['openingPercentage'],
                                                    valveSize=output['valveSize'], fd=output['fd'], Ff=output['Ff'],
                                                    Fp=output['Fp'], Flp=output['Flp'], ratedCv=output['ratedCv'], 
                                                    ar=output['ar'], kc=output['kc'], reNumber=output['reNumber'],
                                                    spl=output['spl'], pipeInVel=output['pipeInVel'],pipeOutVel=output['pipeOutVel'],
                                                    chokedDrop=output['chokedDrop'], valveVel=output['valveVel'],
                                                    fl=output['fl'], tex=output['tex'], powerLevel=output['powerLevel'],
                                                    criticalPressure=output['criticalPressure'], inletPipeSize=output['inletPipeSize'],
                                                    outletPipeSize=output['outletPipeSize'], item=item_selected, iPipe=None
                                                    )
                            item_selected.flowrate_unit = output['fl_unit_form']
                            item_selected.inpres_unit = output['iPresUnit_form']
                            item_selected.outpres_unit = output['oPresUnit_form']
                            item_selected.intemp_unit = output['iTempUnit_form']
                            item_selected.vaporpres_unit = output['vPresUnit_form']
                            item_selected.valvesize_unit = output['vSizeUnit_form']
                            item_selected.inpipe_unit = output['iPipeUnit_form']
                            item_selected.outpipe_unit = output['oPipeUnit_form']  
                            item_selected.criticalpres_unit = output['cPressureUnit']   

                            
                            db.session.add(new_case)
                            db.session.commit()
                        except Exception as e:
                            print(e)
                            new_case = caseMaster(flowrate=a['flowrate'][k], inletPressure=a['inletPressure'][k], fluid=fluid_element,
                                                    outletPressure= a['outletPressure'][k], specificGravity=a['specificGravity'][k],
                                                    inletTemp=a['inletTemp'][k], vaporPressure=a['vaporPressure'][k],
                                                    valveSize=a['vSize'][0], kinematicViscosity=a['kinematicViscosity'][k],
                                                    criticalPressure=a['criticalPressure'][0], inletPipeSize=a['inletPipeSize'][0],
                                                    outletPipeSize=a['outletPipeSize'][0], ratedCv=a['ratedCV'][0], fl=a['fl'][k], xt=a['xt'][k],
                                                    item=item_selected, iPipe=None)
                            item_selected.flowrate_unit = a['flowrate_unit'][0]
                            item_selected.inpres_unit = a['inpres_unit'][0]
                            item_selected.outpres_unit = a['outpres_unit'][0]
                            item_selected.intemp_unit = a['temp_unit'][0]
                            item_selected.vaporpres_unit = a['vaporpres_unit'][0]
                            item_selected.valvesize_unit = a['valvesize_unit'][0]
                            item_selected.inpipe_unit = a['inpipe_unit'][0]
                            item_selected.outpipe_unit = a['outpipe_unit'][0]  
                            item_selected.criticalpres_unit = a['criticalpres_unit'][0]   
                            
 
                            db.session.add(new_case)
                            db.session.commit()
                        
                        # for i in itemCases_1:
                        #     print('deleteing casees')
                        #     db.session.delete(i)
                        #     db.session.commit()

                    flash_message = "Calculation Complete"
                    flash_category = "success"
                except ValueError:
                    flash_message = "Data Incomplete"
                    flash_category = "error"
                except Exception as e:
                    print(e)
                    flash_message = f"Something Went Wrong"
                    flash_category = "error"

                flash(flash_message, flash_category)
                # print(data)
                print(a)
                # print(f"The calculated Cv is: {result}")
                # print(a)
                return redirect(url_for('valveSizing', item_id=item_id, proj_id=proj_id))
        elif f_state == 'Gas':
                # logic to choose which formula to use - using units of flowrate and sg

                len_cases_input = len(a['inletPressure'])
                # print(f'KKKKKKKKKKKSSSSS {a['flowrate'][0]}')
                
                try:
                    for k in range(len_cases_input):
                        try: 
                            print(f'IIIIIIIIIIIIIIIIIIIIIIIIIIIiii')
                            print(a['flowrate'][k], a['flowrate_unit'][0], a['inletPressure'][k],
                                                    a['inpres_unit'][0],
                                                    a['outletPressure'][k], a['outpres_unit'][0],
                                                    a['inletTemp'][k], a['temp_unit'][0], '1', 'pa',
                                                    a['specificHeatRatio'][k], '1',
                                                    a['xt'][k], a['criticalPressure'][0], a['criticalpres_unit'][0], a['inletPipeSize'][0],
                                                    a['inpipe_unit'][0], a['iSch'][0],
                                                    a['outletPipeSize'][0], a['outpipe_unit'][0], a['oSch'][0], 7800,
                                                    5000, a['vSize'][0],
                                                    a['valvesize_unit'][0], a['vSize'][0], a['valvesize_unit'][0], a['ratedCV'][0],
                                                    rw_noise, item_selected, a['mw_sg'][0], a['compressibility'][k], a['molecularWeight'][k], 
                                                    fluid_element.fluidName, i_pipearea_element, valve_element, port_area_)
                            output = getOutputsGas(a['flowrate'][k], a['flowrate_unit'][0], a['inletPressure'][k],
                                                    a['inpres_unit'][0],
                                                    a['outletPressure'][k], a['outpres_unit'][0],
                                                    a['inletTemp'][k], a['temp_unit'][0], '1', 'pa',
                                                    a['specificHeatRatio'][k], '1',
                                                    a['xt'][k], a['criticalPressure'][0], a['criticalpres_unit'][0], a['inletPipeSize'][0],
                                                    a['inpipe_unit'][0], a['iSch'][0],
                                                    a['outletPipeSize'][0], a['outpipe_unit'][0], a['oSch'][0], 7800,
                                                    5000, a['vSize'][0],
                                                    a['valvesize_unit'][0], a['vSize'][0], a['valvesize_unit'][0], a['ratedCV'][0],
                                                    rw_noise, item_selected, a['mw_sg'][0], a['compressibility'][k], a['molecularWeight'][k], 
                                                    fluid_element.fluidName, i_pipearea_element, valve_element, port_area_)
                            sch_element = db.session.query(pipeArea).filter_by(schedule=a['iSch'][0], nominalPipeSize=float(output['inletPipeSize'])).first()
                            new_case = caseMaster(flowrate=output['flowrate'], inletPressure=output['inletPressure'],
                                                    outletPressure=output['outletPressure'],
                                                    inletTemp=output['inletTemp'], specificGravity=output['specificGravity'],
                                                    vaporPressure=output['vaporPressure'], kinematicViscosity=output['kinematicViscosity'], 
                                                    molecularWeight=output['molecularWeight'],
                                                    valveSize=output['valveSize'],
                                                    calculatedCv=output['calculatedCv'], openingPercentage=output['openingPercentage'],
                                                    spl=output['spl'],
                                                    chokedDrop=output['chokedDrop'], reNumber=output['reNumber'],
                                                    xt=output['xt'], tex=output['tex'],
                                                    criticalPressure=output['criticalPressure'], inletPipeSize=output['inletPipeSize'],
                                                    outletPipeSize=output['outletPipeSize'], powerLevel=output['powerLevel'],
                                                    Fp=output['Fp'], fk=output['fk'], y_expansion=output['y'], xtp=output['xtp'],
                                                    fd=output['fd'], ratedCv=output['ratedCv'], ar=output['ar'], kc=output['kc'],
                                                    pipeInVel=output['pipeInVel'], pipeOutVel=output['pipeOutVel'], valveVel=output['valveVel'],
                                                    seatDia=output['seatDia'], machNoUp=output['machNoUp'], machNoDown=output['machNoDown'], machNoValve=output['machNoVel'],
                                                    sonicVelUp=output['sonicVelUp'], sonicVelDown=output['sonicVelDown'],
                                                    sonicVelValve=output['sonicVelValve'], outletDensity=output['outletDensity'], fluid=fluid_element,
                                                    item=item_selected, specificHeatRatio=a['specificHeatRatio'][0], compressibility=a['compressibility'][0], iPipe=None)
                            

                            item_selected.flowrate_unit = output['fl_unit_form']
                            item_selected.inpres_unit = output['iPresUnit_form']
                            item_selected.outpres_unit = output['oPresUnit_form']
                            item_selected.intemp_unit = output['iTempUnit_form']
                            item_selected.vaporpres_unit = output['vPresUnit_form']
                            item_selected.valvesize_unit = output['vSizeUnit_form']
                            item_selected.inpipe_unit = output['iPipeUnit_form']
                            item_selected.outpipe_unit = output['oPipeUnit_form']  
                            item_selected.criticalpres_unit = output['cPressureUnit'] 

                            db.session.add(new_case)
                            db.session.commit()
                        except:
                            new_case = caseMaster(flowrate=a['flowrate'][k], inletPressure=a['inletPressure'][k],
                                                    outletPressure= a['outletPressure'][k],
                                                    inletTemp=a['inletTemp'][k], fluid=fluid_element,
                                                    molecularWeight=a['molecularWeight'][k],
                                                    valveSize=a['vSize'][0], fl=a['fl'][k], xt=a['xt'][k],
                                                    criticalPressure=a['criticalPressure'][0], inletPipeSize=a['inletPipeSize'][0],
                                                    outletPipeSize=a['outletPipeSize'][0], ratedCv=a['ratedCV'][0],
                                                    item=item_selected, specificHeatRatio=a['specificHeatRatio'][0], compressibility=a['compressibility'][0], iPipe=None)
                            # print(fluid_element.fluidName)
                            db.session.add(new_case)
                            db.session.commit()

                        for i in itemCases_1:
                            print('deleteing casees')
                            db.session.delete(i)
                            db.session.commit()
                    flash_message = "Calculation Complete"
                    flash_category = "success"
                except ValueError:
                    flash_message = f"Data Incomplete"
                    flash_category = "error"
                except Exception as e:
                    flash_message = f"Something Went Wrong"
                    flash_category = "error"
            
                flash(flash_message, flash_category)
                return redirect(url_for('valveSizing', item_id=item_id, proj_id=proj_id))

        else:
            flash("No Computation for Two-Phase", "error")
            return redirect(url_for('valveSizing', item_id=item_id, proj_id=proj_id))

 
        
        # return f"<p>{a}</p>"
    try:
        if valve_element.state.name == 'Liquid':
            html_page = 'valvesizing.html'
        else:
            html_page = 'valvesizinggas.html'
    except:
        html_page = 'valvesizing.html'
    
    return render_template(html_page, item=getDBElementWithId(itemMaster, int(item_id)), user=current_user,
                           metadata=metadata_, page='valveSizing', valve=valve_element, case_length=range(6), 
                           cases=itemCases_1, total_length=len(itemCases_1), constants=constants)


@app.route('/item-case-delete/proj-<proj_id>/item-<item_id>/<case_id>', methods=['GET', 'POST'])
def itemCaseDelete(proj_id, item_id, case_id):
    case_ = getDBElementWithId(caseMaster, case_id)
    db.session.delete(case_)
    db.session.commit()
    return redirect(url_for('valveSizing', item_id=item_id, proj_id=proj_id))


@app.route('/item-delete/proj-<proj_id>/item-<item_id>', methods=['GET', 'POST'])
def itemDelete(proj_id, item_id):
    item_ = getDBElementWithId(itemMaster, item_id)
    cases = db.session.query(caseMaster).filter_by(item=item_).all()
    len_cases = len(cases)
    item_nots = db.session.query(itemNotesData).filter_by(item=item_).all()
    len_itn = len(item_nots)
    # redirect to page showing number of cases that are deleted and ask for confirmation
    # Valve details, valve sizing, accessories, actuator sizing, item notes
    # If okay, check whether it is the last case and intimate that one new blank item will be added and redirected to that last item page
    if request.method == 'POST':
        all_items = db.session.query(itemMaster).filter_by(project=item_.project).all()
        total_no_of_items = len(all_items)
        if total_no_of_items == 1:
            new_item = addNewItem(item_.project, 1, "A")
            flash("Blank Item Added, and item deleted successfully")
            
            db.session.delete(item_)
            db.session.commit()
            return redirect(url_for('home', item_id=new_item.id, proj_id=new_item.project.id))
        else:
            db.session.delete(item_)
            db.session.commit()
            all_items = db.session.query(itemMaster).filter_by(project=item_.project).all()
            flash("Item deleted successfully")
            return redirect(url_for('home', item_id=all_items[0].id, proj_id=all_items[0].project.id))
        
    return render_template('deleteConfirmation.html', item_id=item_id, proj_id=proj_id, 
                           item=getDBElementWithId(itemMaster, int(item_id)), user=current_user,
                           len_cases=len_cases, len_itn=len_itn)


@app.route('/project-delete/proj-<proj_id>/item-<item_id>', methods=['GET', 'POST'])
def projectDelete(proj_id, item_id):
    project_ = getDBElementWithId(projectMaster, proj_id)
    items_ = db.session.query(itemMaster).filter_by(project=project_).all()
    len_items = len(items_)
    len_cases = 0
    len_itn = 0
    for len_ in items_:
        item_ = getDBElementWithId(itemMaster, len_.id)
        cases = db.session.query(caseMaster).filter_by(item=item_).all()
        len_cases_ = len(cases)
        len_cases += len_cases_
        item_nots = db.session.query(itemNotesData).filter_by(item=item_).all()
        len_itn_ = len(item_nots)
        len_itn += len_itn_
    # redirect to page showing number of cases that are deleted and ask for confirmation
    # Valve details, valve sizing, accessories, actuator sizing, item notes
    # If okay, check whether it is the last case and intimate that one new blank item will be added and redirected to that last item page
    if request.method == 'POST':
        all_projects = db.session.query(projectMaster).filter_by(user=current_user).all()
        total_no_of_projects = len(all_projects)
        if total_no_of_projects == 1:
            new_project = newUserProjectItem(current_user)
            new_item = db.session.query(itemMaster).filter_by(project=new_project).first()
            flash("Blank Project Added, and project deleted successfully")
            
            db.session.delete(project_)
            db.session.commit()
            return redirect(url_for('home', item_id=new_item.id, proj_id=new_project.id))
        else:
            db.session.delete(project_)
            db.session.commit()
            all_projects = db.session.query(projectMaster).filter_by(user=current_user).all()
            new_item = db.session.query(itemMaster).filter_by(project=all_projects[0]).first()
            flash("Project deleted successfully")
            return redirect(url_for('home', item_id=new_item.id, proj_id=all_projects[0].id))
        
    return render_template('projectDeleteConfirmation.html', item_id=item_id, proj_id=proj_id, 
                           item=getDBElementWithId(itemMaster, int(item_id)), user=current_user,
                           len_cases=len_cases, len_itn=len_itn, len_items=len_items)

###

def interpolate(data, x_db, y_db, vtype):
    x_list = [x_db.one, x_db.two, x_db.three, x_db.four, x_db.five, x_db.six, x_db.seven, x_db.eight, x_db.nine,
              x_db.ten]
    y_list = [y_db.one, y_db.two, y_db.three, y_db.four, y_db.five, y_db.six, y_db.seven, y_db.eight, y_db.nine,
              y_db.ten]
    opening = interpolate_percent(data, x_db, vtype)
    diff = opening - (opening // 10) * 10
    print(f"FL list: {y_list}")
    if x_list[0] < data < x_list[-1]:
        a = 0
        while True:
            # print(f"Cv1, C: {Cv1[a], C}")
            if x_list == data:
                return y_list[a]
            elif x_list[a] > data:
                break
            else:
                a += 1

        # value_interpolate = y_list[a - 1] - (
        #         ((x_list[a - 1] - data) / (x_list[a - 1] - x_list[a])) * (y_list[a - 1] - y_list[a]))
        if diff >= 5:
            value_interpolate = y_list[a]
        else:
            value_interpolate = y_list[a - 1]

        return round(value_interpolate, 4)
    else:
        return 0.5


def interpolate_fd(data, x_db, y_db, vtype):
    x_list = [x_db.one, x_db.two, x_db.three, x_db.four, x_db.five, x_db.six, x_db.seven, x_db.eight, x_db.nine,
              x_db.ten]
    y_list = [y_db.one, y_db.two, y_db.three, y_db.four, y_db.five, y_db.six, y_db.seven, y_db.eight, y_db.nine,
              y_db.ten]
    # print(f"FL list: {y_list}")

    opening = interpolate_percent(data, x_db, vtype)
    diff = opening - (opening // 10) * 10
    if x_list[0] < data < x_list[-1]:
        a = 0
        while True:
            # print(f"Cv1, C: {Cv1[a], C}")
            if x_list[a] == data:
                return y_list[a]
            elif x_list[a] > data:
                break
            else:
                a += 1

        if diff >= 5:
            value_interpolate = y_list[a]
        else:
            value_interpolate = y_list[a - 1]
        # print(f"fd: {value_interpolate}, a: {a}")
        # print(f"diff:{diff}, opening: {opening}, interpolates: {y_list[a]}, {y_list[a - 1]}")

        return round(value_interpolate, 3)
    else:
        return 0.5


def interpolate_percent(data, x_db, vtype):
    x_list = [x_db.one, x_db.two, x_db.three, x_db.four, x_db.five, x_db.six, x_db.seven, x_db.eight, x_db.nine,
              x_db.ten]
    if vtype.lower() == 'globe':
        y_list = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    else:
        y_list = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    if x_list[0] < data < x_list[-1]:
        a = 0
        while True:
            # print(f"Cv1, C: {Cv1[a], C}")
            if x_list == data:
                break
            elif x_list[a] > data:
                break
            else:
                a += 1
        # print(f"percentage: {y_list[a - 1]}, a:{a}")

        value_interpolate = y_list[a - 1] - (
                ((x_list[a - 1] - data) / (x_list[a - 1] - x_list[a])) * (y_list[a - 1] - y_list[a]))

        print(y_list[a - 1], x_list[a - 1], x_list[a], y_list[a], data)

        return round(value_interpolate, 3)
    else:
        return 60



@app.route('/select-valve/proj-<proj_id>/item-<item_id>', methods=['GET', 'POST'])
def selectValve(proj_id, item_id):
    metadata_ = metadata()
    item_selected = getDBElementWithId(itemMaster, item_id)
    valve_element = db.session.query(valveDetailsMaster).filter_by(item=item_selected).first()
    flow_character = valve_element.flowCharacter__.name
    cases = db.session.query(caseMaster).filter_by(item=item_selected).all()
    trim_element = db.session.query(trimType).filter_by(id=valve_element.trimTypeId).first()
    print(f"Select Valve: Len of cases is {len(cases)}")
    if request.method == "POST":
        if len(cases) > 0:
            if request.form.get('getv'):
                print('post')
                cv_all = cvValues.query.all()
                db.session.commit()
                print(len(cv_all))
                data = request.form.to_dict(flat=False)
                a = jsonify(data).json
                print(a)

                vType = getDBElementWithId(valveStyle, a['style'][0]) 
                trimType_ = getDBElementWithId(trimType, a['trimType'][0])  
                flowChara = getDBElementWithId(flowCharacter, a['flowcharacter'][0])
                flowDirec = getDBElementWithId(flowDirection, a['flowdirection'][0])
                rating_v = getDBElementWithId(ratingMaster, a['rating'][0])

                cv_values = []
                for i in cases:
                    cv_value = i.calculatedCv
                    if cv_value:
                        cv_values.append(cv_value)
                min_cv = min(cv_values)
                max_cv = max(cv_values)
                print(f"CV Values: {cv_values}")
                if cv_values.count(None) != len(cv_values):
                # update changes in valve details
                    valve_element.trimType__ = trimType_
                    valve_element.flowCharater__ = flowChara
                    valve_element.flowDirection__ = flowDirec
                    valve_element.rating = rating_v
                    valve_element.style = vType
                    db.session.commit()
                    return_globe_data = []
                    cv__lists = db.session.query(cvTable).filter_by(trimType_=trimType_, flowCharacter_=flowChara, flowDirection_=flowDirec, rating_c=rating_v, style=vType).all()
                    
                    cv_id_lists = [cv_.id for cv_ in cv__lists]
                    cv_lists = cvValues.query.filter(cvValues.cvId.in_(cv_id_lists)).all()
                    for i in cv_lists:
                        seat_bore = i.seatBore
                        travel = i.travel
                        i_list = [i.one, i.two, i.three, i.four, i.five, i.six, i.seven,
                                    i.eight,
                                    i.nine, i.ten, 0.89, travel, seat_bore, i.id, i.cv.valveSize]
                        return_globe_data.append(i_list)
                    # print(return_globe_data)
                    # cv_dummy = last_case.CV
                    # print(cv_dummy)
                    index_to_remove = []
                    for i in return_globe_data:
                        if i[0] < min_cv < i[9]:
                            a = 0
                            while True:
                                if i[a] == min_cv:
                                    break
                                elif i[a] > min_cv:
                                    break
                                else:
                                    a += 1
                            i.append(a)
                            # print(a)
                            # print('CV in Range')
                            # print(i)
                        if i[0] < max_cv < i[9]:
                            b = 0
                            while True:
                                if i[b] == max_cv:
                                    break
                                elif i[b] > max_cv:
                                    break
                                else:
                                    b += 1
                            i.append(b)
                            # print(a)
                            # print('CV in Range')
                            # print(i)
                        else:
                            i.append(10)
                            i.append(10)
                            index_to_remove.append(return_globe_data.index(i))
                            # print(f"Index to remove: {index_to_remove}")
                            # print('CV not in range')
                    for i in return_globe_data:
                        if len(i) == 16:
                            index_to_remove.append(return_globe_data.index(i))
                    # print(f"Index to remove final: {index_to_remove}")
                    for ele in sorted(index_to_remove, reverse=True):
                        del return_globe_data[ele]

                    # print(f'The final return globe is: {return_globe_data}')

                    return render_template('selectvalve.html', item=getDBElementWithId(itemMaster, int(item_id)), valve_data=return_globe_data,
                                            page='selectValve',metadata=metadata_, user=current_user, valve=valve_element)
                else:
                    flash('No CV available to get valves')
                    return render_template('selectvalve.html', item=getDBElementWithId(itemMaster, int(item_id)), valve_data=[],
                                            page='selectValve',metadata=metadata_, user=current_user, valve=valve_element)

                
            elif request.form.get('select'):
                cases_new = db.session.query(caseMaster).filter_by(item=item_selected).all()
                for case_ in cases_new:
                    print('getting cases')
                    print(case_.id)
                    if case_.calculatedCv:
                        print('printing cases id')
                        print(case_.id)
                        valve_d_id = getDBElementWithId(cvValues, request.form.get('valve'))
                        print(f'valve_id_cv {valve_d_id.id}')
                        cv_element = valve_d_id.cv
                        rated_cv_for_case = valve_d_id.ten
                        # Adding valve id in new table
                        case_.cv = valve_d_id.cv
                        # db.session.commit()

                        valve_style = getValveType(valve_element.style.name)
                        # RW Noise
                        if valve_style == 'globe':
                            rw_noise = 0.25
                        else:
                            rw_noise = 0.5
                        # ## done adding
                        print(f'SELECTVALVESS {item_selected.inpres_unit}')
                        seatDia, seatDiaUnit, sosPipe, densityPipe, rw_noise, fl_unit, iPresUnit, oPresUnit, vPresUnit, cPresUnit, iPipeUnit, oPipeUnit, vSizeUnit, iPipeSchUnit, oPipeSchUnit, iTempUnit, sg_choice = case_.seatDia, item_selected.valvesize_unit, 5000, 7800, rw_noise, item_selected.flowrate_unit, item_selected.inpres_unit, item_selected.outpres_unit, item_selected.vaporpres_unit, item_selected.criticalpres_unit, item_selected.inpipe_unit,item_selected.outpipe_unit,item_selected.valvesize_unit,item_selected.valvesize_unit,item_selected.valvesize_unit,item_selected.intemp_unit, case_.mw_sg
                        select_dict = db.session.query(cvValues).filter_by(cv=cv_element, coeff='Cv').first()
                        select_dict_fl = db.session.query(cvValues).filter_by(cv=cv_element, coeff='FL').first()
                        select_dict_xt = db.session.query(cvValues).filter_by(cv=cv_element, coeff='Xt').first()
                        select_dict_fd = db.session.query(cvValues).filter_by(cv=cv_element, coeff='Fd').first()
                        print(select_dict_fl.one)

                        v_size = round(meta_convert_P_T_FR_L('L', cv_element.valveSize, 'inch', 'inch', 1000))
                        # get cv for o_percent
                        # get valveType from valveDetails
                        valve_type_ = valve_element.style.name

                        fl = interpolate(case_.calculatedCv, select_dict, select_dict_fl, valve_type_)
                        xt = interpolate(case_.calculatedCv, select_dict, select_dict_xt, valve_type_)
                        fd = interpolate_fd(case_.calculatedCv, select_dict, select_dict_fd, valve_type_)
                        rated_cv_tex = select_dict.ten
                        last_case = case_
                        print(f"GGGGGGGGGGGGGGGGGGGGGGGAAAAAAAAAAAAASSSSSS {iPresUnit}")
                        if valve_element.state.name == 'Liquid':
                            print(f'FINALCVLIQ {iPresUnit}')
                            final_cv = getCVresult(fl_unit, last_case.specificGravity, iPresUnit, last_case.inletPressure,
                                                last_case.flowrate,
                                                last_case.outletPressure,
                                                oPresUnit, vPresUnit, last_case.vaporPressure, cPresUnit,
                                                last_case.criticalPressure,
                                                last_case.inletPipeSize,
                                                iPipeUnit, last_case.outletPipeSize, oPipeUnit, v_size, 'inch',
                                                last_case.inletTemp,
                                                select_dict.ten, fl, fd,
                                                last_case.kinematicViscosity, iTempUnit)
                        else:
                            print(f'FINALCVGAS {iPresUnit}')
                            final_cv = getCVGas(fl_unit, last_case.specificGravity, last_case.mw_sg, last_case.inletPressure, iPresUnit,
                                                last_case.outletPressure, oPresUnit, v_size, 'inch',
                                                last_case.flowrate, last_case.inletTemp, iTempUnit, select_dict.ten,
                                                last_case.inletPipeSize, iPipeUnit, last_case.outletPipeSize, oPipeUnit, xt,
                                                last_case.compressibility,
                                                last_case.molecularWeight)
                        # print(f"last_cv: {final_cv}")
                        fl = interpolate(final_cv, select_dict, select_dict_fl, valve_type_)
                        xt = interpolate(final_cv, select_dict, select_dict_xt, valve_type_)
                        fd = interpolate_fd(final_cv, select_dict, select_dict_fd, valve_type_)

                        if valve_element.state.name == 'Liquid':
                            final_cv1 = getCVresult(fl_unit, last_case.specificGravity, iPresUnit, last_case.inletPressure,
                                                last_case.flowrate,
                                                last_case.outletPressure,
                                                oPresUnit, vPresUnit, last_case.vaporPressure, cPresUnit,
                                                last_case.criticalPressure,
                                                last_case.inletPipeSize,
                                                iPipeUnit, last_case.outletPipeSize, oPipeUnit, v_size, 'inch',
                                                last_case.inletTemp,
                                                select_dict.ten, fl, fd,
                                                last_case.kinematicViscosity, iTempUnit)
                        else:
                            final_cv1 = getCVGas(fl_unit, last_case.specificGravity, last_case.mw_sg, last_case.inletPressure, iPresUnit,
                                                last_case.outletPressure, oPresUnit, v_size, 'inch',
                                                last_case.flowrate, last_case.inletTemp, iTempUnit, select_dict.ten,
                                                last_case.inletPipeSize, iPipeUnit, last_case.outletPipeSize, oPipeUnit, xt,
                                                last_case.compressibility,
                                                last_case.molecularWeight)
                        print(final_cv1)
                        o_percent = interpolate_percent(final_cv1, select_dict, valve_type_)
                        fl = interpolate(final_cv1, select_dict, select_dict_fl, valve_type_)
                        xt = interpolate(final_cv1, select_dict, select_dict_xt, valve_type_)
                        fd = interpolate_fd(final_cv1, select_dict, select_dict_fd, valve_type_)
                        print('SSSSSSSSSSSSGGGGGGGGGGGG')
                        # print('final fl, xt, select dict')
                        # print(fl, xt, select_dict_xt.id)
                        # print('percentage opening data: gas')
                        # print(o_percent, final_cv1, select_dict)

                        seat_bore = valve_d_id.seatBore
                        travel = valve_d_id.travel

                        fluidName_ = ''
                        try:
                            i_pipearea_element = db.session.query(pipeArea).filter_by(nominalPipeSize=float(last_case.inletPipeSize)).first()
                        except:
                            i_pipearea_element = None
                        try:
                            port_area_ = db.session.query(portArea).filter_by(v_size=int(last_case.valveSize), trim_type="contour",
                                                            flow_char="equal").first()
                        except:
                            port_area_ = None
                        try:
                            valvearea_element = db.session.query(valveArea).filter_by(rating=valve_element.rating.name[5:],
                                                                    nominalPipeSize=float(last_case.inletPipeSize)).first()
                        except:
                            valvearea_element = None

                        # try:
                        #     trimtype = valve_element.trimType__.name
                        # except:
                        #     trim_element = db.session.query(trimType).filter_by(id=valve_element.trimTypeId).first()
                        #     db.session.commit()
                        #     trimtype = trim_element.name
                        trimtype = 'Ported'
                        # flow_character = flow_character
                        if valve_element.state.name == 'Liquid':
                            # try:
                            #     sch_element = db.session.query(pipeArea).filter_by(schedule='std', nominalPipeSize=float(last_case.inletPipeSize)).first()
                            # except:
                            #     sch_element = None
                            output = liqSizing(last_case.flowrate, last_case.specificGravity, last_case.inletPressure, last_case.outletPressure,
                                    last_case.vaporPressure, last_case.criticalPressure, last_case.outletPipeSize,
                                    last_case.inletPipeSize,
                                    v_size, last_case.inletTemp, final_cv1, fl,
                                    last_case.kinematicViscosity, seat_bore, 'inch', sosPipe, densityPipe, rw_noise,
                                    item_selected,
                                    fl_unit, iPresUnit, oPresUnit, vPresUnit, cPresUnit, iPipeUnit, oPipeUnit, 'inch',
                                    'std', iPipeSchUnit, 'std', oPipeSchUnit, iTempUnit,
                                    o_percent, fd, travel, rated_cv_tex, fluidName_, valve_d_id.cv, i_pipearea_element, 
                                    valve_element, port_area_, valvearea_element)
                            new_case = caseMaster(flowrate=output['flowrate'], inletPressure=output['inletPressure'],
                                        outletPressure=output['outletPressure'],
                                        inletTemp=output['inletTemp'], specificGravity=output['specificGravity'],
                                        vaporPressure=output['vaporPressure'], kinematicViscosity=output['kinematicViscosity'],
                                        calculatedCv=output['calculatedCv'], openingPercentage=output['openingPercentage'],
                                        valveSize=output['valveSize'], fd=output['fd'], Ff=output['Ff'],
                                        Fp=output['Fp'], Flp=output['Flp'], ratedCv=rated_cv_for_case, 
                                        ar=output['ar'], kc=output['kc'], reNumber=output['reNumber'],
                                        spl=output['spl'], pipeInVel=output['pipeInVel'],pipeOutVel=output['pipeOutVel'], valveVel=output['valveVel'],
                                        chokedDrop=output['chokedDrop'],
                                        fl=output['fl'], tex=output['tex'], powerLevel=output['powerLevel'], fluid=last_case.fluid,
                                        criticalPressure=output['criticalPressure'], inletPipeSize=output['inletPipeSize'],
                                        outletPipeSize=output['outletPipeSize'], item=item_selected, cv=cv_element, iPipe=None)

                            db.session.add(new_case)
                            db.session.commit()

                            # return redirect(url_for('valveSizing', item_id=item_selected.id, proj_id=item_selected.project.id))
                            
                        else:
                            
                            result_dict = gasSizing(last_case.inletPressure, last_case.outletPressure, last_case.inletPipeSize, last_case.outletPipeSize,
                                    v_size,
                                    last_case.specificGravity, last_case.flowrate, last_case.inletTemp, final_cv1, last_case.compressibility,
                                    last_case.vaporPressure,
                                    seat_bore, 'inch',
                                    sosPipe, densityPipe, last_case.criticalPressure, last_case.kinematicViscosity, item_selected,
                                    fl_unit,
                                    iPresUnit,
                                    oPresUnit, vPresUnit, iPipeUnit, oPipeUnit, 'inch',
                                    'std',
                                    iPipeSchUnit, 'std', oPipeSchUnit, iTempUnit, xt, last_case.molecularWeight,
                                    sg_choice, o_percent, fd, travel, rated_cv_tex,fluidName_, valve_d_id.cv, i_pipearea_element, 
                                    valve_element, port_area_, trimtype, flow_character)
                            db.session.commit()
                            new_case = caseMaster(flowrate=result_dict['flowrate'], inletPressure=result_dict['inletPressure'],
                                outletPressure=result_dict['outletPressure'],
                                inletTemp=result_dict['inletTemp'], specificGravity=result_dict['specificGravity'],
                                vaporPressure=result_dict['vaporPressure'], kinematicViscosity=result_dict['kinematicViscosity'],
                                molecularWeight=last_case.molecularWeight, y_expansion=result_dict['y'],
                                calculatedCv=result_dict['calculatedCv'], openingPercentage=result_dict['openingPercentage'],
                                spl=result_dict['spl'], pipeInVel=result_dict['pipeInVel'], pipeOutVel=result_dict['pipeOutVel'],
                                valveVel=result_dict['valveVel'], specificHeatRatio=last_case.specificHeatRatio,
                                chokedDrop=result_dict['chokedDrop'],
                                xt=result_dict['xt'],tex=result_dict['tex'],
                                powerLevel=result_dict['powerLevel'],
                                criticalPressure=result_dict['criticalPressure'], inletPipeSize=result_dict['inletPipeSize'],
                                outletPipeSize=result_dict['outletPipeSize'],
                                item=item_selected, fk=result_dict['fk'], xtp=result_dict['xtp'], ratedCv=rated_cv_for_case,
                                fd=result_dict['fd'], Fp=result_dict['Fp'], ar=result_dict['ar'], kc=result_dict['kc'], reNumber=result_dict['reNumber'],
                                machNoUp=result_dict['machNoUp'], machNoDown=result_dict['machNoDown'], machNoValve=result_dict['machNoVel'],
                                sonicVelUp=result_dict['sonicVelUp'], sonicVelDown=result_dict['sonicVelDown'],
                                sonicVelValve=result_dict['sonicVelValve'], outletDensity=result_dict['outletDensity'],x_delp=result_dict['x_delp'],
                                cv=valve_d_id.cv, iPipe=None, valveSize=v_size, compressibility=last_case.compressibility)
                            # new_case = caseMaster()
                            db.session.add(new_case)
                            db.session.commit()

                for case_ in cases_new:
                    print('deleting cases')
                    print(case_.id)
                    db.session.delete(case_)
                    db.session.commit()
                return redirect(url_for('valveSizing', item_id=item_id, proj_id=proj_id))
                    
        else:
            flash('Add Case to select valve')
            return redirect(url_for('selectValve', item_id=item_id, proj_id=proj_id))
    return render_template('selectvalve.html', item=getDBElementWithId(itemMaster, int(item_id)), user=current_user,
                           metadata=metadata_, page='selectValve', valve=valve_element, valve_data=[])


@app.route('/saveStrokeCV')
def saveStrokeCV():
    cvFill = request.args.get('cvFill')
    cvExhaust = request.args.get('cvExhaust')
    act_case = request.args.get('act_case')

    act_case_element = getDBElementWithId(actuatorCaseData,int(act_case))
    stroke_element = db.session.query(strokeCase).filter_by(actuatorCase_=act_case_element).first()

    stroke_element.combinedCVFill = cvFill 
    stroke_element.combinedCVExhaust = cvExhaust 
    db.session.commit()
    print(f'SAVEVEVVEVEV {cvFill},{cvExhaust},{act_case_element}')
    return "SUCCESS"

@app.route('/calculateStrokeCV')
def calculateStrokeCV():
    cvFill_ = json.loads(request.args.get('cvFill'))
    cvExhaust_ = json.loads(request.args.get('cvExhaust'))
    cvFill = [float(val) for val in cvFill_ if val]
    cvExhaust = [float(val) for val in cvExhaust_ if val]
    # Clean up the elements and remove empty strings
    # cvFill_ = [value.strip('"') for value in cvFill if value.strip()]
    # cvExhaust_ = [value.strip('"') for value in cvExhaust if value.strip()]


    print(f'strokecalculation {cvFill},{cvExhaust}')  
    cvFillList = 1 / math.sqrt(sum([(1 / i) * (1 / i) for i in cvFill]))
    cvExhaustList = 1 / math.sqrt(sum([(1 / i) * (1 / i) for i in cvExhaust]))



    print(f'cvFillcvExhaustKKK {cvFillList} , {cvExhaustList}')
  
    return jsonify({
        'cvFill': round(cvFillList,3),
        'cvExhaust': round(cvExhaustList,3)
        })


# Actuator Sizing
@app.route('/actuator-sizing/proj-<proj_id>/item-<item_id>', methods=['GET', 'POST'])
def actuatorSizing(proj_id, item_id):
    item_element = getDBElementWithId(itemMaster, int(item_id))
    valve_element = db.session.query(valveDetailsMaster).filter_by(item=item_element).first()
    act_element = db.session.query(actuatorMaster).filter_by(item=item_element).first()
    metadata_ = metadata()
    if request.method == 'POST':
        actuator_input_dict = {}
        actuator_input_dict['actuatorType'] = [request.form.get('actType')]
        actuator_input_dict['springAction'] = [request.form.get('failAction')]
        actuator_input_dict['handWheel'] = [request.form.get('mount')]
        actuator_input_dict['adjustableTravelStop'] = [request.form.get('travel')]
        actuator_input_dict['orientation'] = [request.form.get('orientation')]
        actuator_input_dict['availableAirSupplyMin'] = [request.form.get('availableAirSupplyMin')]
        actuator_input_dict['availableAirSupplyMax'] = [request.form.get('availableAirSupplyMax')]
        # print(actuator_input_dict)
        if request.form.get('sliding'):
            print('working')
            act_element.update(actuator_input_dict, act_element.id)
            return redirect(url_for('slidingStem', item_id=item_id, proj_id=proj_id))
        elif request.form.get('rotary'):
            act_element.update(actuator_input_dict, act_element.id)
            return redirect(url_for('rotaryActuator', item_id=item_id, proj_id=proj_id))
        elif request.form.get('stroketime'):
            act_element.update(actuator_input_dict, act_element.id)
            return redirect(url_for('strokeTime', item_id=item_id, proj_id=proj_id))
        else:
            pass
    return render_template('actuatorSizing.html', item=getDBElementWithId(itemMaster, int(item_id)), user=current_user,
                           metadata=metadata_, page='actuatorSizing', valve=valve_element, act=act_element)


@app.route('/slidingStemDel')
def slidingStemDel():
    act_id = request.args.get('act_id')
    actMaster = getDBElementWithId(actuatorMaster,act_id)
    act_element = db.session.query(actuatorCaseData).filter_by(actuator_=actMaster)\
        .filter(actuatorCaseData.valveThrustClose != None )\
        .first()
    print(f'ACTELEMENT {act_element}')
    if act_element:
        db.session.delete(act_element)
        db.session.commit()
        print('success')
        return "SUCCESS"
    else:
        print('fail')
        return "FAIL"


@app.route('/slidingStemDelete/proj-<proj_id>/item-<item_id>/act-<act_id>',methods=['GET','POST'])
def slidingStemDelete(proj_id,item_id,act_id):
    actMaster = getDBElementWithId(actuatorMaster,act_id)
    act_element = db.session.query(actuatorCaseData).filter_by(actuator_=actMaster).first()
    print(f'ACTELEMENT {act_element}')
    db.session.delete(act_element)
    db.session.commit()
    return redirect(url_for('slidingStem', item_id=item_id, proj_id=proj_id))

@app.route('/removeTrim')
def removeTrim():
    act_case_id = request.args.get('act_case_id')
    print(f'TTTTTTTTT {act_case_id}')
    act_case = getDBElementWithId(actuatorCaseData,act_case_id)
    act_case.seatDia = None
    db.session.commit()
    

    # db.session.query(actuatorCaseData).filter_by()
    return "SUCCESS"


@app.route('/get_rotaryinputs')
def get_rotaryinputs():
    valve_size = request.args.get('valve_size')
    disc_dia = request.args.get('disc_dia')
    seatId = request.args.get('seatId')
    seat_element = getDBElementWithId(seat, seatId)
    seating_element = db.session.query(seatingTorque)\
            .filter_by(valveSize=valve_size)\
            .order_by(func.abs(seatingTorque.discDia - disc_dia))\
            .first()

    if seat_element.name == 'PTFE':
        a_factor = seating_element.softSeatA
        b_factor = seating_element.softSeatB 
    else:
        a_factor = seating_element.metalSeatA
        b_factor = seating_element.metalSeatB 

    data = {
        'afac': float(a_factor),
        'bfac': float(b_factor),
        'cusc': float(seating_element.cusc),
        'cusp': float(seating_element.cusp)
    }
    

    return jsonify(data) 


        

    
    






@app.route('/getUaElement')
def getUaElement():
    seatDia = request.args.get('seatDia')
    itemId = request.args.get('itemId')
    item_element = getDBElementWithId(itemMaster,itemId)
    valve_element = db.session.query(valveDetailsMaster).filter_by(item=item_element).first()
    ua_element = db.session.query(unbalanceAreaTb).filter_by(trimType_=valve_element.trimType__,seatLeakageClass__=valve_element.seatLeakageClass__)\
    .order_by(func.abs(unbalanceAreaTb.seatDia - seatDia))\
    .first()

    print(f'getUA {valve_element.trimType__},{valve_element.seatLeakageClass__},{seatDia}')
    data = {
        'plugDia':ua_element.plugDia,
        'ua':ua_element.Ua
    }
    print(f'ua {data}')
    return data

def actuatorForce(size, stroke, r1, r2, setPressure):
    springRate = ((r2 - r1) / stroke) * size
    springForceMin = r1 * size
    springForceMax = r2 * size
    NATMax = size * setPressure - springForceMin
    NATMin = size * setPressure - springForceMax
    # print(
    #     f"act forces: spring rate: {round(springRate)}, spring force min: {round(springForceMin)}, spring force max: {round(springForceMax)}, Net Air Thrust Max: {round(NATMax)}, Net Air Thrust Min: {round(NATMin)}")
    return [round(springRate), round(springForceMin), round(springForceMax), round(NATMax), round(NATMin)]


def compareForces(p1, p2, d1, d2, d3, ua, rating, material, leakageClass, trimtype, balance, flow,
                  case, shutoffDelP, size, stroke, r1, r2, setPressure, failAction, valveTravel, flowChar, act_type,packingF,seatF):
    
    print(f'After Selecting actuator')
    print(p1, p2, d1, d2, d3, ua, rating, material, leakageClass, trimtype, balance, flow,
                  case, shutoffDelP, size, stroke, r1, r2, setPressure, failAction, valveTravel, flowChar, act_type)

    if stroke > valveTravel:
        stroke = valveTravel

    vForce_ = valveForces(p1, p2, d1, d2, d3, ua, rating, material, leakageClass, trimtype, balance, flow,
                          case, shutoffDelP,packingF,seatF)
    vForce_shutoff_ = valveForces(p1, p2, d1, d2, d3, ua, rating, material, leakageClass, trimtype, balance, flow,
                                  'shutoff', shutoffDelP,packingF,seatF)
    vForce_open_ = valveForces(p1, p2, d1, d2, d3, ua, rating, material, leakageClass, trimtype, balance, flow,
                               'open', shutoffDelP,packingF,seatF)
    vForce_close_ = valveForces(p1, p2, d1, d2, d3, ua, rating, material, leakageClass, trimtype, balance, flow,
                                'close', shutoffDelP,packingF,seatF)

    vForce = shutoffDelP
    # vForce_shutoff = vForce_shutoff_[0]
    # vForce_open = vForce_open_[0]
    # vForce_close = vForce_close_[0]
    setPressure_ = meta_convert_P_T_FR_L('P', setPressure, 'bar (a)',
                            'psia (g)', 1.0 * 1000)
    print(f'aForce {size},{stroke},{r1},{r2},{setPressure_}')
    aForce = actuatorForce(float(size), float(stroke), float(r1), float(r2), float(setPressure_))
    springrate = aForce[0]
    sfMin = aForce[1]
    sfMax = aForce[2]
    natMax = aForce[3]
    natMin = aForce[4]

    print(f'FORCE {vForce},{aForce}')

    with app.app_context():
        if d1 in [1, 3, 8, 11, 4]:
            d1 = round(d1)
        friction_element = db.session.query(packingFriction)\
            .filter_by(rating=rating)\
            .filter_by(packing_=material)\
            .order_by((func.abs(packingFriction.stemDia - d3)))\
            .first()
        

        print(f'FRICTION ELEMENT {friction_element}')
        # packing_material = friction_element.
        # a_ = {'ptfe1': friction_element.ptfe1, 'ptfe2': friction_element.ptfe2, 'ptfer': friction_element.ptfer,
        #       'graphite': friction_element.graphite}
        # sf_element = db.session.query(seatLoad).filter_by(trimtype=trimtype, seatBore=d1).first()
        # b_ = {'six': sf_element.six, 'two': sf_element.two, 'three': sf_element.three, 'four': sf_element.four,
        #       'five': sf_element.five}
        print(f"trimtype and d1: {trimtype}, {d1}")
        sf_element = db.session.query(seatLoadForce)\
            .filter_by(trimType_=trimtype,leakage=leakageClass)\
            .order_by(func.abs(seatLoadForce.seatBore - d1))\
            .first()
        
        B = float(friction_element.value)
        C = math.pi * d1 * float(sf_element.value)
        # get kn value for balanced under case
        kn_element = db.session.query(knValue)\
            .filter_by(flowDirection_=flow, flowCharacter_=flowChar, trimType_=trimtype)\
            .order_by(func.abs(knValue.portDia - d1))\
            .first()
        if kn_element:
            kn_value = float(kn_element.value)
        else:
            kn_value = 0
        print(f"Packing friction: {B}, Seat Load Force: {round(C, 3)}, kn value: {kn_value}")
        print(f"Kn inputs: portDia: {d1}, flow direction: {flow}, flow character: {flowChar}, trim type: {trimtype}, balance: {balance}")
    # print(f"Valve Forces: Shutoff: {vForce_shutoff}, Shutoff+: {vForce}, Open: {vForce_open}, Close: {vForce_close}")
    
    result, comment1, comment2, comment3 = None, None, None, None
    if vForce < 0:
        del_P = (aForce[1] - B - C) / vForce_[1]
        if aForce[0] > (2 * vForce_[1] / valveTravel) * del_P:
            pass
    ks = springrate
    if balance.name == 'Unbalanced' and flow.name == 'Under':
        kn = 0
    elif balance.name == 'Balanced' and flow.name == 'Over':
        kn = 0
    elif balance.name == 'Unbalanced' and flow.name == 'Over':
        kn = (2 * vForce_[1] / valveTravel)
    else:
        if kn_value == 0:
            kn = (2 * vForce_[1] / valveTravel)
        else:
            kn = kn_value
    # print(f"Unbalanced area: {vForce_[1]}")

    # Gross force
    gross_ = float(size) * float(setPressure)

    if act_type == 'Piston with Spring':
        if failAction == 'AFC':
            if (gross_ - sfMax) > vForce:
                case1 = True
                comment1 = f"(gross_ - sfMax)  > vForce: {(gross_ - sfMax)} > {vForce}"
            else:
                case1 = False
                comment1 = f"(gross_ - sfMax)  < vForce: {(gross_ - sfMax)} < {vForce}"

            if gross_ + sfMin > vForce:
                comment2 = f'Spring Force Min: {gross_ + sfMin}, valveForce: {vForce}'
                case2 = True
            else:
                comment2 = f'Spring Force Min: {gross_ + sfMin}, valveForce: {vForce}'
                case2 = False

            if vForce:
                a_ = ((sfMin - B - C) / vForce_[1]) * kn

                if ks > a_:
                    comment3 = f"KS: {ks} is greater than delP*KN: {a_}, kn: {kn}, delP: {round(((sfMin - B - C) / vForce_[1]), 2)}"
                else:
                    comment3 = f"KS: {ks} is not greater than delP*KN: {a_}, kn: {kn}, delP: {round(((sfMin - B - C) / vForce_[1]), 2)}"
            if case1 and case2:
                result = 'Pass'
            else:
                result = f"Fail{case1}, {case2}"
        else:
            if gross_ + sfMin > vForce:
                case1 = True
                comment1 = f"gross_ + sfMin > vForce: {gross_ + sfMin} > {vForce}"
            else:
                case1 = False
                comment1 = f"gross_ + sfMin < vForce: {gross_ + sfMin} < {vForce}"

            if (gross_ - sfMax) > vForce:
                comment2 = f'(gross_ - sfMax): {(gross_ - sfMax)}, valveForce: {vForce}'
                case2 = True
            else:
                comment2 = f'(gross_ - sfMax): {(gross_ - sfMax)}, valveForce: {vForce}'
                case2 = False

            a_ = ((natMin - B - C) / vForce_[1]) * kn
            if ks > a_:
                comment3 = f"KS: {ks} is greater than delP*KN: {a_}, kn: {kn}, delP: {round(((natMin - B - C) / vForce_[1]), 2)}"
            else:
                comment3 = f"KS: {ks} is not greater than delP*KN: {a_}, kn: {kn}, delP: {round(((natMin - B - C) / vForce_[1]), 2)}"

            if case1 and case2:
                result = 'Pass'
            else:
                result = f"Fail{case1}, {case2}"
    else:
        if failAction == 'AFC':
            print(f'CompareForceS____ {natMin},{B},{sfMin},{vForce}')
            if natMin > B:
                case1 = True
                comment1 = f"natMin > Friction force: {natMin} > {B}"
            else:
                case1 = False
                comment1 = f"natMin < Friction force: {natMin} < {B}"

            if sfMin > vForce:
                comment2 = f'Spring Force Min: {sfMin}, valveForce: {vForce}'
                case2 = True
            else:
                comment2 = f'Spring Force Min: {sfMin}, valveForce: {vForce}'
                case2 = False

            if vForce:
                a_ = ((sfMin - B - C) / vForce_[1]) * kn

                if ks > a_:
                    comment3 = f"KS: {ks} is greater than delP*KN: {a_}, kn: {kn}, delP: {round(((sfMin - B - C) / vForce_[1]), 2)}"
                else:
                    comment3 = f"KS: {ks} is not greater than delP*KN: {a_}, kn: {kn}, delP: {round(((sfMin - B - C) / vForce_[1]), 2)}"
            if case1 and case2:
                result = 'Pass'
            else:
                result = f"Fail{case1}, {case2}"
        else:
            if sfMin > B:
                case1 = True
                comment1 = f"sfMin > Friction force: {sfMin} > {B}"
            else:
                case1 = False
                comment1 = f"sfMin < Friction force: {sfMin} < {B}"

            if natMin > vForce:
                comment2 = f'Net Air Thrust Min: {natMin}, valveForce: {vForce}'
                case2 = True
            else:
                comment2 = f'Net Air Thrust Min: {natMin}, valveForce: {vForce}'
                case2 = False

            a_ = ((natMin - B - C) / vForce_[1]) * kn
            if ks > a_:
                comment3 = f"KS: {ks} is greater than delP*KN: {a_}, kn: {kn}, delP: {round(((natMin - B - C) / vForce_[1]), 2)}"
            else:
                comment3 = f"KS: {ks} is not greater than delP*KN: {a_}, kn: {kn}, delP: {round(((natMin - B - C) / vForce_[1]), 2)}"

            if case1 and case2:
                result = 'Pass'
            else:
                result = f"Fail{case1}, {case2}"

    result_list = [result, springrate, sfMax, sfMin, natMax, natMin, B, C, vForce, vForce_shutoff_, vForce_close_,
                vForce_open_, comment1, comment2, comment3, kn, sf_element.value]
    print(f'RESULT_ACT {result_list}')


    print(result_list)
    return result_list






@app.route('/sliding-stem/proj-<proj_id>/item-<item_id>', methods=['GET', 'POST'])
def slidingStem(proj_id, item_id):
    item_element = getDBElementWithId(itemMaster, int(item_id))
    try:
        cases = db.session.query(caseMaster).filter_by(item=item_element).all()
        cv_element = db.session.query(cvValues).filter_by(cv=cases[0].cv).first()
        selected_sized_valve_element = db.session.query(cvTable).filter_by(id=cases[0].cv.id).first()
        # balancing_element = db.session.query(balancing).filter_by(id=selected_sized_valve_element.balancingId).first() 
       
        stemDiaDrop = db.session.query(stemSize).filter_by(valveSize=cases[0].valveSize).all()
        
        print(len(cases))
        print(f'KSKKSKS {cv_element}')
        print(cv_element.seatBore)
    except:
        cv_element = None
        selected_sized_valve_element = None
        balancing_element = None

    act_element = db.session.query(actuatorMaster).filter_by(item=item_element).first()
    act_case_data = db.session.query(actuatorCaseData).filter_by(actuator_=act_element).first()
    if not act_case_data:
        new_act_case_data = actuatorCaseData(actuator_=act_element)
        db.session.add(new_act_case_data)
        db.session.commit()
        act_case_data = new_act_case_data

    valve_element = db.session.query(valveDetailsMaster).filter_by(item=item_element).first()
    ua_element = db.session.query(unbalanceAreaTb)\
        .filter_by(trimType_=valve_element.trimType__,seatLeakageClass__=valve_element.seatLeakageClass__)\
        .order_by(func.abs(unbalanceAreaTb.seatDia - cv_element.seatBore))\
        .first()
    trimType_element = db.session.query(trimType).filter_by(id=valve_element.trimTypeId).first()
    fl_d_element = db.session.query(flowDirection).filter_by(id=valve_element.flowDirectionId).first()
    print(f'UNNHHSHSHHSSH {valve_element.balanceSeal__}')
    if valve_element.balanceSeal__.name == 'Unbalanced':
        balancing_element = db.session.query(balancing).filter_by(name='Unbalanced').first() 
    else:
        balancing_element = db.session.query(balancing).filter_by(name='Balanced').first() 
    
    metadata_ = metadata()
    # print(selected_sized_valve_element.balancing_.name)
    if request.method == 'POST':
        actuator_input_dict = {}
        actuator_input_dict['actuatorType'] = [request.form.get('actType')]
        actuator_input_dict['springAction'] = [request.form.get('failAction')]
        actuator_input_dict['handWheel'] = [request.form.get('mount')]
        actuator_input_dict['adjustableTravelStop'] = [request.form.get('travel')]
        actuator_input_dict['orientation'] = [request.form.get('orientation')]
        actuator_input_dict['availableAirSupplyMin'] = [request.form.get('availableAirSupplyMin')]
        actuator_input_dict['availableAirSupplyMax'] = [request.form.get('availableAirSupplyMax')]
        actuator_input_dict['availableAirSupplyMaxUnit'] = [request.form.get('availableAirSupplyMaxUnit')]
        actuator_input_dict['setPressureUnit'] = [request.form.get('setPressureUnit')]
        print(f'ACT {actuator_input_dict}')
        if request.form.get('sliding'):
            print('working')
            act_element.update(actuator_input_dict, act_element.id)
            return redirect(url_for('slidingStem', item_id=item_id, proj_id=proj_id))
        elif request.form.get('rotary'):
            act_element.update(actuator_input_dict, act_element.id)
            return redirect(url_for('rotaryActuator', item_id=item_id, proj_id=proj_id))
        elif request.form.get('stroketime'):
            # act_element.update(actuator_input_dict, act_element.id)
            return redirect(url_for('strokeTime', item_id=item_id, proj_id=proj_id))
        elif request.form.get('submit1'):
            # print('req sbumit 1 working')
            actuator_input_dict_2 = {}
            actuator_input_dict_2['actuatorType'] = [request.form.get('actType')]
            actuator_input_dict_2['springAction'] = [request.form.get('failAction')]
            actuator_input_dict_2['handWheel'] = [request.form.get('mount')]
            actuator_input_dict_2['adjustableTravelStop'] = [request.form.get('travel')]
            actuator_input_dict_2['orientation'] = [request.form.get('orientation')]
            actuator_input_dict_2['availableAirSupplyMin'] = [request.form.get('availableAirSupplyMin')]
            actuator_input_dict_2['availableAirSupplyMax'] = [request.form.get('availableAirSupplyMax')]
            actuator_input_dict_2['availableAirSupplyMaxUnit'] = [request.form.get('availableAirSupplyMaxUnit')]
            actuator_input_dict_2['setPressureUnit'] = [request.form.get('setPressureUnit')]
            act_element.update(actuator_input_dict, act_element.id)
            data = request.form.to_dict(flat=False)
            a = jsonify(data).json
            print(a)
            print(f'IIIIIISSSSSSSSs {a['stemDia'][0]}')
            stemsize_ = getDBElementWithId(stemSize,a['stemDia'][0])
            
            print(f'IIIIIISBBBB {stemsize_}')
            stem_fraction = float(Fraction(''.join(str(stemsize_.stemDia))))
            print(f'HHHHHHHHHHHHHHHHHHHh {stemsize_},{stem_fraction}')
            
            # Inputs conversion
            valveSize = meta_convert_P_T_FR_L('L', float(a['valveSize'][0]), a['valveSizeUnit'][0],
                                        'inch', 1.0 * 1000)
            plugDia = meta_convert_P_T_FR_L('L', float(a['plugDia'][0]), a['plugDiaUnit'][0],
                                        'inch', 1.0 * 1000)
            stemDia = meta_convert_P_T_FR_L('L', stem_fraction, a['stemDiaUnit'][0],
                                        'inch', 1.0 * 1000)
            ua =  meta_convert_P_T_FR_L('A', float(a['ua'][0]), a['unbalanceAreaUnit'][0],
                                        'inch2', 1.0 * 1000)
            seatDia = meta_convert_P_T_FR_L('L', float(a['seatDia'][0]), a['seatDiaUnit'][0],
                                        'inch', 1.0 * 1000)
            
            stroke = meta_convert_P_T_FR_L('L', float(a['valveTravel'][0]), a['valveTravelUnit'][0],
                                        'inch', 1.0 * 1000)
            iPressure = meta_convert_P_T_FR_L('P', float(a['iPressure'][0]), a['inletPressureUnit'][0],
                                        'psia (g)', 1.0 * 1000)
            oPressure = meta_convert_P_T_FR_L('P', float(a['oPressure'][0]), a['outletPressureUnit'][0],
                                        'psia (g)', 1.0 * 1000)
            print(f'B$$$$$$$$ {a['shutOffDelP'][0]}, {a['shutoffDelPUnit'][0]}')
            shutOffDelP = meta_convert_P_T_FR_L('P', float(a['shutOffDelP'][0]), str(a['shutoffDelPUnit'][0])+" (a)",
                                        'psia (g)', 1.0 * 1000)
            print(f'LLLLLLLLLLL {shutOffDelP}')
            stemDiaDrop = db.session.query(stemSize).filter_by(valveSize=valveSize).all()
            # Call case data update function here.
            act_case_data_json = {}
            act_case_data_json['valveSize'] = a["valveSize"]
            act_case_data_json['plugDia'] = a["plugDia"]
            act_case_data_json['stemDia'] = a["stemDia"]
            act_case_data_json['unbalanceArea'] = a["ua"]
            act_case_data_json['seatDia'] = a["seatDia"]
            act_case_data_json['iPressure'] = a["iPressure"]
            act_case_data_json['oPressure'] = a["oPressure"]
            act_case_data_json['valveTravel'] = a["valveTravel"]
            act_case_data_json['trimTypeId'] = a["trimType"]
            act_case_data_json['balancingId'] = a["balancing"]
            act_case_data_json['flowDirectionId'] = a["flowDirection"]
            act_case_data_json['packingFriction'] = a['packingF']
            act_case_data_json['seatloadFactor'] = a['seatF']
            act_case_data_json['shutOffDelP'] = a['shutOffDelP']
            act_case_data_json['balancingId'] = a['balancing']
            # act_case_data_json['shutOffDelP'] = a['shutOffDelP']
            # balance = a['balancing']
            print(f'PACKINGSSS {a['packingF']},{ a['packingFrictionUnit']}')   
            packingF = meta_convert_P_T_FR_L('F', float(a['packingF'][0]), a['packingFrictionUnit'][0],
                                        'lbf',
                                        1000)
            trimType__ = getDBElementWithId(trimType,a["trimType"][0])
            balancing__ = getDBElementWithId(balancing,a["balancing"][0]) 
            flowDirection__ = getDBElementWithId(flowDirection,a["flowDirection"][0])
            # act_case_data_json['unbalForce'] = a['unbalForce']
            # act_case_data_json['negGrad'] = a['negGrad']


            act_case_data_json['valveSizeUnit'] = a['valveSizeUnit']
            act_case_data_json['seatDiaUnit'] = a['seatDiaUnit']
            act_case_data_json['unbalanceAreaUnit'] = a['unbalanceAreaUnit']
            act_case_data_json['stemDiaUnit'] = a['stemDiaUnit']
            act_case_data_json['plugDiaUnit'] = a['plugDiaUnit']
            act_case_data_json['valveTravelUnit'] = a['valveTravelUnit']
            act_case_data_json['packingFrictionUnit'] = a['packingFrictionUnit']
            act_case_data_json['inletPressureUnit'] = a['inletPressureUnit']
            act_case_data_json['outletPressureUnit'] = a['outletPressureUnit']
            act_case_data_json['unbalForceOpenUnit'] = a['unbalForceOpenUnit']
            act_case_data_json['negativeGradientUnit'] = a['negativeGradientUnit']
            act_case_data_json['delPFlowingUnit'] = a['delPFlowingUnit']
            # act_case_data_json['unbalForceOpenUnit'] = a['unbalForceOpenUnit']
            # act_case_data_json['negativeGradientUnit'] = a['negativeGradientUnit']
            # print(f'iiiiiiiisjsjsjsjsjj {act_case_data_json}')

            act_case_data.update(act_case_data_json, act_case_data.id)
            # print(f'PPPASSS {a['balancing'][0]}')
            # if int(a['balancing'][0]) == 1:
            #     balance = 'Balanced'
            # elif int(a['balancing'][0]) == 2:
            #     balance = 'Unbalanced'
            # else:
            #     balance = 'Unbalanced'
            # print(f'KSKKSKSK {balance}')

            # Calculations
            valve_forces = valveForces(iPressure, oPressure, seatDia, plugDia, stem_fraction, ua, valve_element.rating, valve_element.packing__,
                                        valve_element.seatLeakageClass__, trimType__, balancing__, flowDirection__, 'shutoff+', shutOffDelP,packingF,a['seatF'][0])
            vf_shutoff = valveForces(iPressure, oPressure, seatDia, plugDia, stem_fraction, ua, valve_element.rating, valve_element.packing__,
                                        valve_element.seatLeakageClass__, trimType__, balancing__, flowDirection__, 'shutoff', shutOffDelP,packingF,a['seatF'][0])
            vf_open = valveForces(iPressure, oPressure, seatDia, plugDia, stem_fraction, ua, valve_element.rating, valve_element.packing__,
                                        valve_element.seatLeakageClass__, trimType__, balancing__, flowDirection__, 'open', shutOffDelP,packingF,a['seatF'][0])
            vf_close = valveForces(iPressure, oPressure, seatDia, plugDia, stem_fraction, ua, valve_element.rating, valve_element.packing__,
                                        valve_element.seatLeakageClass__, trimType__, balancing__,flowDirection__, 'close', shutOffDelP,packingF,a['seatF'][0])
            v_shutoff, v_shutoff_plus, v_open, v_close = round(vf_shutoff[0]), round(valve_forces[0]), round(
                vf_open[0]), round(vf_close[0])
            
            # balance_element = getDBElementWithId(balancing, a["balancing"])
            # flow_element = getDBElementWithId(flowDirection,a["flowDirection"])
            # if balance_element.name == 'Unbalanced' and flow_element.name == 'Under':
            #     kn = 0
            # elif balance_element.name == 'Balanced' and flow_element.name == 'Over':
            #     kn = 0 #(table)
            # elif balance_element.name == 'Unbalanced' and flow_element.name == 'Over':
            #     kn = (2 * a["ua"] ) / valveTravel
            # else:
            #     if kn_value == 0:
            #         kn = (2 * iPressure / valveTravel)
            #     else:
            #         kn = kn_value

            packing_fric = valve_forces[2]
            seatload_fact = valve_forces[3]

            packing_friction = valve_forces[4]
            seat_load_force = valve_forces[5]
            print(v_shutoff)
            # store data in v_details
            # valve_element.valve_size = f"{balance}#{stroke}#{round(seatDia, 3)}#{plugDia}#{stemDia}#{ua}#{v_shutoff}#{v_shutoff_plus}#{v_open}#{v_close}#{packing_fric}#{seatload_fact}"
            db.session.commit()
            v_data = [v_shutoff, v_shutoff_plus, v_open, v_close]
            print(v_data, packing_fric, seatload_fact)
            act_case_data_json_result = {}
            act_case_data_json_result['valveThrustClose'] = [v_shutoff_plus]
            act_case_data_json_result['valveThrustOpen'] = [v_open]
            act_case_data_json_result['shutOffForce'] = [round(valve_forces[6],2)]
            act_case_data_json_result['valveThrustCloseUnit'] = ['lbf']
            act_case_data_json_result['valveThrustOpenUnit'] = ['lbf']
            act_case_data_json_result['shutOffForceUnit'] = ['lbf']
            print(f'shutff {v_shutoff_plus}')

            act_case_data.update(act_case_data_json_result, act_case_data.id)

            act_case_data.packingF = packing_friction
            act_case_data.seatLoad = seat_load_force
            db.session.commit()
            # act_case_data = db.session.query(actuatorCaseData).filter_by(actuator_=act_element).all()
            # if len(act_case_data) == 0:
            #     new_act = actuatorCaseData(actuator_=act_element)
            #     db.session.add(new_act)
            #     db.session.commit()
            
            # act_case_data_ = db.session.query(actuatorCaseData).filter_by(actuator_=act_element).first()
            
            # get data again
            # data__ = [valve_element.trimType__.name, valve_element.flowDirection__.name, cases[0].valveSize, cv_element.seatBore, iPressure, oPressure, shutOffDelP,
            #             iPressure - oPressure]
            return redirect(url_for('slidingStem', item_id=item_id, proj_id=proj_id))
        
        elif request.form.get('select-actuator-sliding'):
          
                
            data = request.form.to_dict(flat=False)
            a = jsonify(data).json
            print(f'slidingactuator {a}')
            

            setPressure = float(request.form.get('availableAirSupplyMax'))
            setPressureUnit = a['setPressureUnit'][0]
            setPressure = meta_convert_P_T_FR_L('P', setPressure, setPressureUnit,
                                        'psia (g)', 1.0 * 1000)
            # shutoff_plus = float(request.form.get('shutoffDelP'))
  
            shutoff_plus_ = float(a['valveThrustClose'][0])
            valveOpen_ = float(a['valveThrustOpen'][0])
            shutOffForce_ = float(a['shutOffForce'][0])

            vclose_unit_ = a['valvecloseUnit'][0]
            valveopenUnit_ = a['valveopenUnit'][0]
            shutoffUnit_ = a['shutoffUnit'][0]
            # print(f'SHHHHHHHHSHSHS {shutoff_plus_}')

            shutoffplus_force = meta_convert_P_T_FR_L('F', shutoff_plus_, vclose_unit_,
                                        'lbf',
                                        1000)
            valveopen_force = meta_convert_P_T_FR_L('F', valveOpen_, valveopenUnit_,
                            'lbf',
                            1000)
            shutoff_force = meta_convert_P_T_FR_L('F', shutOffForce_, shutoffUnit_,
                    'lbf',
                    1000)


            # stem_dia = float(request.form.get('stemDia'))
            # valveTravel = request.form.get('travel')
            data = request.form.to_dict(flat=False)
            a = jsonify(data).json
            # seatDia = float(request.form.get('seatDia'))WW
            # act_dat_prev = v_details.serial_no
            # fail_action_prev = act_dat_prev.split('#')[1]
            # act_type = act_dat_prev.split('#')[0]
            # actuator_data = db.session.query(actuatorDataVol).filter_by(SFMax=stem_dia,
            #                                                             failAction=fail_action_prev,
            #                                                             SFMin=act_type).all()
            valveTravel = a['valveTravel'][0]
            
            stemsize_ = getDBElementWithId(stemSize,a['stemDia'][0])
            stem_fraction = float(Fraction(''.join(str(stemsize_.stemDia))))
            print(f'DAATASSII {a['failAction'][0]},{stem_fraction},{a['actType'][0]}')
            actuator_data = db.session.query(slidingActuatorData).filter_by(failAction=a['failAction'][0],stemDia=stem_fraction,actType=a['actType'][0]).all()

            
            # print(f"actuator data lenght: {setPressure},{shutoff_plus},{valveTravel}")
            print(f"LENGTHACT {len(actuator_data)},{setPressure}")
            return_actuator_data = []
            
            for i in actuator_data:
                if float(valveTravel) <= float(i.travel):
                    springRate = float(((float(i.sMax) - float(i.sMin)) / float(i.travel)) * float(i.effectiveArea))
                    print(f'SPring {springRate}')
                    springForceMin = float(i.sMin) * float(i.effectiveArea)
                    springForceMax = float(i.sMax) * float(i.effectiveArea)
                    NATMax = float(i.effectiveArea) * setPressure - springForceMin
                    NATMin = float(i.effectiveArea) * setPressure - springForceMax
                    gross_ = float(i.effectiveArea) * setPressure
                    print(f'ACTTYPE {i.actType}')
                    if i.actType == 'Piston with Spring':
                        if i.failAction == 'AFC':
                            if gross_ + springForceMin > shutoffplus_force:
                                i_list = [i.id, i.actSize, i.travel, i.sMin, i.sMax, i.failAction, int(springRate),
                                            int(springForceMin),
                                            int(springForceMax),
                                            int(NATMax), int(NATMin), i.stemDia]
                                return_actuator_data.append(i_list)
                        elif i.failAction == 'AFO':
                            print(f'GROSS {gross_} {springForceMax} {shutoff_plus_}')
                            if gross_ - springForceMax > shutoffplus_force:
                                i_list = [i.id, i.actSize, i.travel, i.sMin, i.sMax, i.failAction, springRate,
                                            springForceMin,
                                            springForceMax,
                                            NATMax, NATMin, i.stemDia]
                                return_actuator_data.append(i_list)
                    else:
                        if i.failAction == 'AFO':
                            print(f'GROSS {NATMin} {shutoff_plus_}')
                            if NATMin > shutoffplus_force:
                                i_list = [i.id, i.actSize, i.travel, i.sMin, i.sMax, i.failAction, springRate,
                                            springForceMin,
                                            springForceMax,
                                            NATMax, NATMin, i.stemDia]
                                return_actuator_data.append(i_list)
                        elif i.failAction == 'AFC':
                            if springForceMin > shutoffplus_force:
                                i_list = [i.id, i.actSize, i.travel, i.sMin, i.sMax, i.failAction, springRate,
                                            springForceMin,
                                            springForceMax,
                                            NATMax, NATMin, i.stemDia]
                                return_actuator_data.append(i_list)
            print(f'item_d {return_actuator_data}')
            return render_template('select_actuator.html', data=return_actuator_data, item_d=item_element,
                                    setP=setPressure, page='selectActuator', item=item_element, user=current_user)
            

        elif request.form.get('select_act'):
            act_id = request.form.get('valve') 
            act_element_sliding = getDBElementWithId(slidingActuatorData,act_id)
            act_master = db.session.query(actuatorMaster).filter_by(itemId=item_id).first()
            stemsize_ = getDBElementWithId(stemSize,act_case_data.stemDia)
            stem_fraction = float(Fraction(''.join(str(stemsize_.stemDia))))
            iPressure = meta_convert_P_T_FR_L('P', act_case_data.iPressure, act_case_data.inletPressureUnit,
                                        'psia (g)', 1.0 * 1000)
            oPressure = meta_convert_P_T_FR_L('P', act_case_data.oPressure, act_case_data.outletPressureUnit,
                                        'psia (g)', 1.0 * 1000)
            seatDia = meta_convert_P_T_FR_L('L', act_case_data.seatDia, act_case_data.seatDiaUnit,
                            'inch', 1.0 * 1000) 
            plugDia = meta_convert_P_T_FR_L('L', act_case_data.plugDia, act_case_data.plugDiaUnit,
                                        'inch', 1.0 * 1000)
            stemDia = meta_convert_P_T_FR_L('L', stem_fraction, act_case_data.stemDiaUnit,
                                        'inch', 1.0 * 1000)
            ua =  meta_convert_P_T_FR_L('A', act_case_data.unbalanceArea, act_case_data.unbalanceAreaUnit,
                            'inch2', 1.0 * 1000)
            # trimType__ = getDBElementWithId(trimType,a["trimType"][0])
            # balancing__ = getDBElementWithId(balancing,a["balancing"][0]) 
            # flowDirection__ = getDBElementWithId(flowDirection,a["flowDirection"][0])
            # packingF = meta_convert_P_T_FR_L('F', float(a['packingF'][0]), a['packingFrictionUnit'][0],
            #                             'lbf',
            #                             1000)
            act_fun_output = compareForces(iPressure, oPressure, seatDia, plugDia,
                stem_fraction, ua, valve_element.rating, valve_element.packing__,
                valve_element.seatLeakageClass__, act_case_data.trimType_, act_case_data.balancing_,act_case_data.flowDirection_ ,
                'shutoff+', act_case_data.valveThrustClose, act_element_sliding.effectiveArea, act_element_sliding.travel, act_element_sliding.sMin, act_element_sliding.sMax, act_master.availableAirSupplyMax, act_element_sliding.failAction,
                act_case_data.valveTravel, valve_element.flowCharacter__, act_element_sliding.actType,act_case_data.packingFriction,act_case_data.seatloadFactor) 
            # other inputs for page
            stemArea = round((math.pi * float(stemDia) * float(stemDia) / 4), 3)
            actuatorSize_ = act_element_sliding.actSize
            springRate = act_fun_output[1]
            springWindUp = round((act_fun_output[3] / springRate), 2)
            maxSpringLoad = act_fun_output[2]
            frictionBand = round((float(act_fun_output[6]) / float(act_element_sliding.actSize)), 3)
            reqHW = 'none'
           
            # act_initial = v_details.serial_no
            # act_initial_list = act_initial.split('#')
            act_master = db.session.query(actuatorMaster).filter_by(itemId=item_id).first()
            fa = act_element_sliding.failAction
            mount_ = act_master.handWheel
            hw_thrust = db.session.query(hwThrust).filter_by(failAction=fa, mount=mount_, ac_size=actuatorSize_).first()
            sfMax, sfMin, natMax, natMin, comment1, comment2, comment3, packing_friction, seatload_force, kn, seatload_factor = \
                act_fun_output[2], act_fun_output[3], act_fun_output[4], act_fun_output[5], act_fun_output[12], \
                act_fun_output[13], act_fun_output[14], act_fun_output[6], act_fun_output[7], act_fun_output[15], \
                act_fun_output[16]
            if hw_thrust:
                maxHW = hw_thrust.max_thrust
            else:
                maxHW = ''
            airsupplyMin =  meta_convert_P_T_FR_L('P', float(act_master.availableAirSupplyMin), act_master.availableAirSupplyMaxUnit,
                                        'psia (g)', 1.0 * 1000)
            airsupplyMax = meta_convert_P_T_FR_L('P', float(act_master.availableAirSupplyMax), act_master.setPressureUnit,
                                        'psia (g)', 1.0 * 1000)
            act_case_data.act_size = actuatorSize_ 
            act_case_data.act_travel = act_element_sliding.travel 
            act_case_data.actuatorTravelUnit = 'inch'
            act_case_data.lower_benchset = act_element_sliding.sMin
            act_case_data.lowerBenchsetUnit = 'psia (g)'
            act_case_data.upper_benchset = act_element_sliding.sMax
            act_case_data.upperBenchSetUnit = 'psia (g)'
            act_case_data.stemArea = stemArea
            act_case_data.stemAreaUnit = 'inch2'
            act_case_data.diaphragm_ea = act_element_sliding.effectiveArea
            act_case_data.effectiveAreaUnit = 'inch2'
            act_case_data.spring_rate = springRate
            act_case_data.springWindUp = springWindUp
            act_case_data.springWindupUnit = 'inch'
            act_case_data.maxSpringLoad = maxSpringLoad
            act_case_data.maximumSpringLoadUnit = 'lbf'
            act_case_data.sfMin = sfMin
            act_case_data.natMin = natMin
            act_case_data.actuatorThrustValveCloseUnit = 'lbf'
            act_case_data.actuatorThrustValveOpenUnit = 'lbf'
            act_case_data.frictionBand = frictionBand 
            act_case_data.act_VO = act_element_sliding.VO
            if maxHW:
                act_case_data.reqHandwheelThrust = maxHW
            act_case_data.airsupply_min = round(airsupplyMin,2)
            act_case_data.maximumAirSupplyUnit = 'psia (g)'
            act_case_data.airsupply_max = round(airsupplyMax,2) 
            act_case_data.setPressureUnit = 'psia (g)'
            act_case_data.knValue = kn
            act_case_data.frictionBandUnit = 'psia (g)'
            act_case_data.reqHandwheelUnit = 'lbf'
            act_case_data.slidingActuatorId = act_element_sliding.id
            

            print(f'KNNNN {kn}')
            db.session.commit()

            # db.session.commit()



            # v_details.rating_v = f"{acSize}#{travel}#{smin}#{smax}#{fail_action}#{setP}#{sfMax}#{sfMin}#{natMax}#{natMin}#{comment1}#{comment2}#{comment3}#{packing_friction}#{round(seatload_force, 2)}#{kn}" \
            #                      f"#{stemArea}#{actuatorSize_}#{springRate}#{springWindUp}#{maxSpringLoad}#{frictionBand}#{reqHW}#{maxHW}#{seatload_factor}"
            # print(
            #     f"{acSize}#{travel}#{smin}#{smax}#{fail_action}#{setP}#{act_fun_output[2]}#{act_fun_output[3]}#{act_fun_output[4]}#{act_fun_output[5]}#{act_fun_output[-1]}#{act_fun_output[-2]}#{act_fun_output[-3]}")
            # # db.session.commit()
            # print(
            #     f'Stroke Speed Data: VO: {act_data.VO}, VM: {act_data.VM}, VS: {int(act_data.VO) - int(act_data.VM)}, Pi Fill: {round(smin + (frictionBand / float(act_data.NATMin)))}, Pf fill: {round(smax + (frictionBand / float(act_data.NATMin)))}, Pi Exhaust: {round(smax - (frictionBand / float(act_data.NATMin)))}, Pf Exhaust: {round(smin - (frictionBand / float(act_data.NATMin)))}')

            # stroke_string = f'{act_case_data.VO}+{act_case_data.VM}+{int(act_data.VO) - int(act_data.VM)}+{(smin + (frictionBand / float(act_data.NATMin)))}+{(smax + (frictionBand / float(act_data.NATMin)))}+{(smax - (frictionBand / float(act_data.NATMin)))}+{(smin - (frictionBand / float(act_data.NATMin)))}'
            # print(stroke_string)
            # v_details.cage_clamp = stroke_string
            db.session.commit()
            return redirect(url_for('slidingStem', item_id=item_id, proj_id=proj_id))
        
           





       
            print(f'AAAACYTTTTTTID  {act_id}')
 
            

        
        else:
            pass
    print(f'CVELEMENTTT {balancing_element.id}')
    return render_template('slidingstem.html', item=getDBElementWithId(itemMaster, int(item_id)), 
                           user=current_user, metadata=metadata_, page='slidingStem', 
                           valve=valve_element, cv=selected_sized_valve_element, act=act_element, 
                           cases=cases,trimtType=trimType_element,fl_d_element=fl_d_element, 
                           cv_element=cv_element, balancing=balancing_element, act_case=act_case_data,stemDiaDrop=stemDiaDrop,ua_element=ua_element)



@app.route('/getStemSize')
def getStemSize():
    valveSize = request.args.get('valveSize')
    print(f'get {valveSize}')
    stemDiaDrop = db.session.query(stemSize).filter_by(valveSize=valveSize).all()
    stem_list = []
    for i in stemDiaDrop:
        stem_dia = {
            'id':i.id,
            'value':i.stemDia
        }
        stem_list.append(stem_dia)


    return stem_list


@app.route('/get_radialaxial')
def get_radialaxial():
    packingId = request.args.get('packingId')
    print(f'GETRADIAL {packingId}')
    packingElement = getDBElementWithId(packing, packingId) 
    if "Graphite" in packingElement.name:
        return "25.2"
    else:
        return "12.9"




@app.route('/rotary-actuator/proj-<proj_id>/item-<item_id>', methods=['GET', 'POST'])
def rotaryActuator(proj_id, item_id):
    item_element = getDBElementWithId(itemMaster, int(item_id))
    act_element = db.session.query(actuatorMaster).filter_by(item=item_element).first()
    valve_element = db.session.query(valveDetailsMaster).filter_by(item=item_element).first()



    try:
        cases = db.session.query(caseMaster).filter_by(item=item_element).all()
        cv_element = db.session.query(cvValues).filter_by(cv=cases[0].cv).first()
    except:
        cv_element = None


    act_case_data = db.session.query(rotaryCaseData).filter_by(actuator_=act_element).first()
    if not act_case_data:
        new_act_case_data = rotaryCaseData(actuator_=act_element)
        db.session.add(new_act_case_data)
        db.session.commit()
        act_case_data = new_act_case_data

    metadata_ = metadata()

    if request.method == 'POST':
        actuator_input_dict = {}
        actuator_input_dict['actuatorType'] = [request.form.get('actType')]
        actuator_input_dict['springAction'] = [request.form.get('failAction')]
        actuator_input_dict['handWheel'] = [request.form.get('mount')]
        actuator_input_dict['adjustableTravelStop'] = [request.form.get('travel')]
        actuator_input_dict['orientation'] = [request.form.get('orientation')]
        actuator_input_dict['availableAirSupplyMin'] = [request.form.get('availableAirSupplyMin')]
        actuator_input_dict['availableAirSupplyMax'] = [request.form.get('availableAirSupplyMax')]
        actuator_input_dict['availableAirSupplyMaxUnit'] = [request.form.get('availableAirSupplyMaxUnit')]
        actuator_input_dict['setPressureUnit'] = [request.form.get('setPressureUnit')]
        # print(actuator_input_dict)
        if request.form.get('sliding'):
            print('working')
            act_element.update(actuator_input_dict, act_element.id)
            return redirect(url_for('slidingStem', item_id=item_id, proj_id=proj_id))
        elif request.form.get('rotary'):
            act_element.update(actuator_input_dict, act_element.id)
            return redirect(url_for('rotaryActuator', item_id=item_id, proj_id=proj_id))
        elif request.form.get('stroketime'):
            act_element.update(actuator_input_dict, act_element.id)
            return redirect(url_for('strokeTime', item_id=item_id, proj_id=proj_id))
        elif request.form.get('rotary_calculate'):
            act_element.update(actuator_input_dict, act_element.id)

        
            data = request.form.to_dict(flat=False)
            data.pop('rotary_calculate')
            data.pop('availableAirSupplyMax')
            data.pop('availableAirSupplyMaxUnit')
            data.pop('availableAirSupplyMin')
            data.pop('shutoffDelP')
            data.pop('actType')
            data.pop('maxAirUnit')
            data.pop('mount')
            data.pop('failAction')
            data.pop('orientation')
            data.pop('setPressureUnit')
            data.pop('shutoffDelPUnit')
            data.pop('travel')
            # data.pop('rotaryCaseData_id')
           
            a = jsonify(data).json
            print(f'ROTARY DATAS {a}')
            


            
            rotary_case_inputs = {}
            # rotary_case_inputs['v_size'] = a['v_size']
            # rotary_case_inputs['valveSizeUnit'] = a['valveSizeUnit']

            # rotary_case_inputs['disc_dia'] = a['disc_dia']
            # rotary_case_inputs['discDiaUnit'] = a['discDiaUnit']

            # rotary_case_inputs['shaft_dia'] = a['shaft_dia']
            # rotary_case_inputs['shaftDiaUnit'] = a['shaftDiaUnit']

            # rotary_case_inputs['max_rot'] = a['max_rot']
            # rotary_case_inputs['max_rotUnit'] = a['max_rotUnit']

            # rotary_case_inputs['delP'] = a['delP']
            # rotary_case_inputs['delpUnit'] = a['delpUnit']

            # rotary_case_inputs['bush_coeff'] = a['bush_coeff']
            # rotary_case_inputs['csc'] = a['csc']
            # rotary_case_inputs['csv'] = a['csv']
            # rotary_case_inputs['a_factor'] = a['a_factor']
            # rotary_case_inputs['b_factor'] = a['b_factor']
            # rotary_case_inputs['pack_coeff'] = a['pack_coeff']
            # rotary_case_inputs['radial_coeff'] = a['radial_coeff']
            # rotary_case_inputs['Section'] = a['Section']


            #op Calc 
            delp = meta_convert_P_T_FR_L('P', float(a['delP'][0]), a['delpUnit'][0],
                                    'bar (a)', 1.0 * 1000)
            section = meta_convert_P_T_FR_L('L', float(a['Section'][0]), a['packingRadialUnit'][0],
                        'inch', 1.0 * 1000)
            shaftDia = meta_convert_P_T_FR_L('L', float(a['shaft_dia'][0]), a['shaftDiaUnit'][0],
                        'inch', 1.0 * 1000)
            discDia = meta_convert_P_T_FR_L('L', float(a['disc_dia'][0]), a['discDiaUnit'][0],
                        'inch', 1.0 * 1000)
            print(f'CALC {delp},{section},{shaftDia},{discDia}')
            seating_torque__ = round((delp * float(a['b_factor'][0])) + float(a['a_factor'][0]))
            packing_torque__ = round(0.75 * delp * math.pi * float(a['radial_coeff'][0]) * section * float(a['pack_coeff'][0]) * (shaftDia ** 2))
            friction_torque__ = round((math.pi / 8) * (discDia ** 2) * delp * shaftDia * float(a['bush_coeff'][0]))
            bto_ = seating_torque__ + packing_torque__ + friction_torque__
            btc_ = round(0.8 * bto_)
            rto_ = eto_ = rtc_ = etc_ = 0.5 * bto_
            shaft_mat = getDBElementWithId(shaft,valve_element.shaftId)
            yeild = db.session.query(shaft).filter_by(name=shaft_mat.name).first()
            print(f'YIELD {yeild}')
            strength = round(int(yeild.yield_strength) / math.sqrt(3))
            a['mast'] = [(math.pi * strength * (shaftDia ** 3)) / 16]
            a['st'] = [seating_torque__]
            a['pt'] = [packing_torque__]
            a['ft'] = [friction_torque__]
            a['bto'] = [bto_]
            a['rto'] = [rto_]
            a['eto'] = [eto_]
            a['btc'] = [btc_]
            a['rtc'] = [rtc_]
            a['etc'] = [etc_ ]
            a['setP'] = [act_element.availableAirSupplyMax]


            act_case_data.update(a, act_case_data.id)

            print(f'ROTARY {data},{a}')





            return redirect(url_for('rotaryActuator', item_id=item_id, proj_id=proj_id,act_case_data=act_case_data))
            
        elif request.form.get('select_Ractuator'):
            print(f'SELECT ACT ROTARY')
            setPressure_ = meta_convert_P_T_FR_L('P', float(act_element.availableAirSupplyMax), act_element.availableAirSupplyMaxUnit,
                        'bar (a)', 1.0 * 1000) 
            bto = meta_convert_P_T_FR_L('TOR', float(act_case_data.bto), act_case_data.btoUnit,
                        'lbf.inch', 1.0 * 1000) 
            rto = meta_convert_P_T_FR_L('TOR', float(act_case_data.rto), act_case_data.rtoUnit,
                        'lbf.inch', 1.0 * 1000) 
            eto = meta_convert_P_T_FR_L('TOR', float(act_case_data.eto), act_case_data.etoUnit,
                        'lbf.inch', 1.0 * 1000) 
            btc = meta_convert_P_T_FR_L('TOR', float(act_case_data.btc), act_case_data.btcUnit,
                        'lbf.inch', 1.0 * 1000) 
            rtc = meta_convert_P_T_FR_L('TOR', float(act_case_data.rtc), act_case_data.rtcUnit,
                        'lbf.inch', 1.0 * 1000) 
            etc = meta_convert_P_T_FR_L('TOR', float(act_case_data.etc), act_case_data.etcUnit,
                        'lbf.inch', 1.0 * 1000) 


            
            
            print(f'SETPRESSURESS {str(setPressure_).rstrip('0').rstrip('.')}')
            print(f'SELECT ACT DATAS {setPressure_}, {''.join(str(act_element.springAction))},{act_element.actuatorType}')
            return_actuator_data = db.session.query(rotaryActuatorData).filter_by(actType=act_element.actuatorType,failAction=act_element.springAction, setPressure=str(setPressure_).rstrip('0').rstrip('.')).all()
            print(f'len_act_data: {len(return_actuator_data)}')
            all_act_data = []
            for acts in return_actuator_data:
                if act_element.springAction == 'DA':
                    if float(acts.start) < bto and float(acts.mid) < rto and float(acts.end) < eto:
                        a_dict = {'id': (acts.id, 0), 'fail_action': acts.failAction,
                                    'valve_interface': acts.valveInterface, 'act_size': acts.actSize_,
                                    'spring_set': acts.springSet, 's1': 'NA', 's2': 'NA',
                                    's3': 'NA', 'a1': acts.start, 'a2': acts.mid, 'a3': acts.end,
                                    'set_pressure': acts.setPressure}
                else:
                    if act_element.springAction == "AFO":
                        bt1 = btc
                        bt2 = bto
                        rt1 = rtc
                        rt2 = rto
                        et1 = etc
                        et2 = eto
                    else:
                        bt2 = btc
                        bt1 = bto
                        rt2 = rtc
                        rt1 = rto
                        et2 = etc
                        et1 = eto
                    if float(acts.start) < bt1 and float(acts.mid) < rt1 and float(acts.end) < et1:
                        st_element = db.session.query(rotaryActuatorData).filter_by(
                            valveInterface=acts.valveInterface, springSet=acts.springSet).first()
                        if st_element:
                            if float(st_element.start) < bt2 and float(st_element.mid) < rt2 and float(
                                    st_element.end) < et2:
                                a_dict = {'id': (acts.id, st_element.id), 'fail_action': acts.failAction,
                                            'valve_interface': acts.valveInterface, 'act_size': acts.actSize_,
                                            'spring_set': acts.springSet, 's1': st_element.start,
                                            's2': st_element.mid,
                                            's3': st_element.end, 'a1': acts.start, 'a2': acts.mid, 'a3': acts.end,
                                            'set_pressure': acts.setPressure}
                            else:
                                pass

                all_act_data.append(a_dict)

                print('bt, rt, et')
               
                print(f'all_act_data {all_act_data}')

                return render_template('select_ractuator.html', data=all_act_data, item_d=item_element,
                        page='selectActuator', item=item_element, user=current_user)
          
    return render_template('RotaryActuatorSizing.html', item=getDBElementWithId(itemMaster, int(item_id)), 
                           user=current_user, metadata=metadata_, page='rotaryActuator',
                         valve=valve_element, act=act_element,act_case_data=act_case_data,cases=cases,cv_element=cv_element)



@app.route('/rotaryActCaseDelete/proj-<proj_id>/item-<item_id>/act-<act_id>',methods=['GET','POST'])
def rotaryActCaseDelete(proj_id,item_id,act_id):
    actMaster = getDBElementWithId(actuatorMaster,act_id)
    act_element = db.session.query(rotaryCaseData).filter_by(actuator_=actMaster).first()
    print(f'ACTELEMENT {act_element}')
    db.session.delete(act_element)
    db.session.commit()
    return redirect(url_for('rotaryActuator', item_id=item_id, proj_id=proj_id))



@app.route('/select-rotary-actuator/proj-<proj_id>/item-<item_id>', methods=['GET', 'POST'])
def selectRotaryActuator(proj_id, item_id):
    item_element = getDBElementWithId(itemMaster, int(item_id))
    act_element = db.session.query(actuatorMaster).filter_by(item=item_element).first()
    act_case_data = db.session.query(rotaryCaseData).filter_by(actuator_=act_element).first()
    if request.method == 'POST':
       
        a_ = request.form.to_dict(flat=True)
        # a_ = jsonify(rAct_.get('rAct')).json
       
        act_data = {}
        b_ = ast.literal_eval(a_['rAct'])
        print(f'SELECT B {b_}')
        
        #outputs 

        act_case_data.springSet = b_['spring_set']
        act_case_data.springSt = b_['s1']
        act_case_data.springMd = b_['s2']
        act_case_data.springEd = b_['s3']
        act_case_data.AirSt = b_['a1']
        act_case_data.AirMd = b_['a2']
        act_case_data.AirEd = b_['a3']
        act_case_data.actSize_ = b_['act_size']
        act_case_data.stStartUnit = 'lbf.inch'
        act_case_data.stMidUnit = 'lbf.inch'
        act_case_data.stEndUnit = 'lbf.inch'
        act_case_data.atStartUnit = 'lbf.inch'
        act_case_data.atMidUnit = 'lbf.inch'
        act_case_data.atEndUnit = 'lbf.inch'
        act_case_data.maxAir = float(act_element.availableAirSupplyMax)
        db.session.commit()                            
        

        return redirect(url_for('rotaryActuator', item_id=item_id, proj_id=proj_id))




def calX(p1,p2):
    
    return ((p1-p2)/p1)


def calY(p1,p2):
    y_result = 1 - (calX(p1,p2)  / (3 * 1 * 0.65))
    print(f'YCALC {y_result}')
    return y_result


def strokeVol(input1, input2):
    print(f'INPUT FOR VOLUME : {input1}, {input2}')
    result = (input1 * input2) / (39.37 * 39.37 * 39.37)
    print(f'VOLUME : {result}')
    return result

def strokeFlowrate(p1,p2,cv):
    print(f'P1: p2 {p1},{p2}')
    Q = (cv * 2240 * 1 * p1 * calY(p1,p2) * math.sqrt(calX(p1,p2) / (28.96 * 1 * 303.15)))
    print(f'FLOWRATE : {Q}')
    return Q


def totalFillStrokep2(p1,piFill,pfFill):
    delp = piFill + (2/3 * (pfFill - piFill))
    return p1 - delp 

def preExhaustStrokep1(piExhaust,setPressure):
    return piExhaust + ((setPressure - piExhaust) / 2)

def totalExhaustStrokep1(pfExhaust,setPressure):
    return pfExhaust + ((setPressure - pfExhaust) / 4)

def CalcStrokeTime(vol,flowrate):
    result = round(((vol / flowrate) * 3600) , 3)
    print(f'Final Result {result}')
    return result



@app.route('/stroke-time/proj-<proj_id>/item-<item_id>', methods=['GET', 'POST'])
def strokeTime(proj_id, item_id):
    item_element = getDBElementWithId(itemMaster, int(item_id))
    valve_element = db.session.query(valveDetailsMaster).filter_by(item=item_element).first()
    act_element_master = db.session.query(actuatorMaster).filter_by(item=item_element).first()
    act_element_case = db.session.query(actuatorCaseData).filter_by(actuator_=act_element_master).first()
    stroke_element = db.session.query(strokeCase).filter_by(actuatorCase_=act_element_case).first()
    # sliding_act = getDBElementWithId(slidingActuatorData, act_element_case.slidingActuatorId)
    clearance_vol = act_element_case.act_VO
    swept_vol = float(act_element_case.diaphragm_ea) * float(act_element_case.act_travel)
    if not stroke_element:
        new_stroke_data = strokeCase(actuatorCase_=act_element_case)
        db.session.add(new_stroke_data)
        db.session.commit()
        stroke_element = new_stroke_data
    print(f'STROKE ELEMENTSVV {act_element_case}')
    # act_VO = db.session.query(slidingActuatorData).filter_by(VO=)

    metadata_ = metadata()
    if act_element_master.actuatorType == 'Piston without Spring':
        html_page = 'stroke_time_piston.html'
    else:
        html_page = 'stroke_time_spring.html'

    if request.method == "POST":
        print(f'PPPPPPPPPSS {request.method}')
        if request.form.get('strokeinput'):
            print("INPUT")
            data = request.form.to_dict() 
            packingFriction_ =  float(data['packingF']) 
            data.pop('strokeinput')
            data.pop('packingF')
            
            a_ = jsonify(data).json
           
            
           


            # stroke_inputs = {} 

            actSize_ = float(data['act_size'])
            diaphragmArea_ = meta_convert_P_T_FR_L('A', float(data['diaphragm_ea']), data['diaphragm_eaUnit'],
                                    'inch2', 1.0 * 1000)
            actTravel_ = meta_convert_P_T_FR_L('L', float(data['act_travel']), data['act_travelUnit'],
                                    'inch', 1.0 * 1000)
            setPressure_ = meta_convert_P_T_FR_L('P', float(data['airsupply_max']), data['airsupply_maxUnit'],
                                    'psia (g)', 1.0 * 1000)
            lower_benchset_ = meta_convert_P_T_FR_L('P', float(data['lower_benchset']), data['lower_benchsetUnit'],
                                    'psia (g)', 1.0 * 1000)
            upper_benchset_ = meta_convert_P_T_FR_L('P', float(data['upper_benchset']), data['upper_benchsetUnit'],
                                    'psia (g)', 1.0 * 1000)
            spring_rate_ = float(data['spring_rate'])
            
            clearanceVol_ = float(data['clearance_vol']) 
            sweptVol_ = float(data['swept_vol']) 




            piExhaust = upper_benchset_ - (packingFriction_ / diaphragmArea_)
            pfExhaust = lower_benchset_ - (packingFriction_ / diaphragmArea_)
            piFill = lower_benchset_ + (packingFriction_ / diaphragmArea_) 
            pfFill = upper_benchset_ + (packingFriction_ / diaphragmArea_)

            a_['piExhaust'] = round(piExhaust,3)
            a_['pfExhaust'] = round(pfExhaust,3)
            a_['piFill'] = round(piFill,3)
            a_['pfFill'] = round(pfFill,3)

            a_['piExhaustUnit'] = 'psia (g)'
            a_['pfExhaustUnit'] = 'psia (g)'
            a_['piFillUnit'] = 'psia (g)'
            a_['pfFillUnit'] = 'psia (g)'


            print(f'STROKE DATASSSSSSSVVV {stroke_element}')
            stroke_element.update(a_, stroke_element.id)
            


            return redirect(url_for('strokeTime', item_id=item_id, proj_id=proj_id, stroke_element=stroke_element))
            
        
        if request.form.get('interstroke'):
            data = request.form.to_dict()
            packingFriction_ =  float(data['packingF']) 
            data.pop('interstroke')
            data.pop('packingF')
            
            a_ = jsonify(data).json
            setPressure_ = meta_convert_P_T_FR_L('P', float(data['airsupply_max']), data['airsupply_maxUnit'],
                        'bar (g)', 1.0 * 1000)
            print(f'DATASXX {data}')
            piExhaust__ =  meta_convert_P_T_FR_L('P', float(data['piExhaust']), data['piExhaustUnit'],
                                        'bar (g)', 1.0 * 1000)
            pfExhaust__ = meta_convert_P_T_FR_L('P', float(data['pfExhaust']), data['pfExhaustUnit'],
                                        'bar (g)', 1.0 * 1000)
            piFill__ = meta_convert_P_T_FR_L('P', float(data['piFill']), data['piFillUnit'],
                            'bar (g)', 1.0 * 1000)
            pfFill__ = meta_convert_P_T_FR_L('P', float(data['pfFill']), data['pfFillUnit'],
                            'bar (g)', 1.0 * 1000)
            print(f'BEFORE CALC {piExhaust__},{pfExhaust__},{piFill__},{pfFill__}')
  
            

            cvFill__ = float(data['combinedCVFill'])
            cvExhaust__ = float(data['combinedCVExhaust'])
            clearanceVol__ = float(data['clearance_vol'])
            sweptVol__ = float(data['swept_vol'])
            totalVol = clearanceVol__ + sweptVol__ 
            


            preFillTime = CalcStrokeTime(strokeVol(piFill__, clearanceVol__), strokeFlowrate(setPressure_,piFill__,cvFill__)) 
            totalFillTime = CalcStrokeTime(strokeVol(pfFill__, totalVol), strokeFlowrate(setPressure_,totalFillStrokep2(setPressure_,piFill__,pfFill__),cvFill__) ) 
            preExhaustTime = CalcStrokeTime(strokeVol(piExhaust__ , totalVol),  strokeFlowrate(preExhaustStrokep1(piExhaust__,setPressure_),0,cvExhaust__))
            totalExhaustTime = CalcStrokeTime(strokeVol(pfExhaust__, sweptVol__), strokeFlowrate(totalExhaustStrokep1(pfExhaust__,setPressure_),0,cvExhaust__)) 
            print(f'RESULTS {preFillTime},{totalFillTime},{preExhaustTime},{totalExhaustTime}')
            print(f'INTERRRRRRRRRRR')
            
            a_['prefillTime'] = preFillTime 
            a_['totalfillTime'] = totalFillTime 
            a_['preExhaustTime'] = preExhaustTime 
            a_['totalExhaustTime'] = totalExhaustTime 

            stroke_element.update(a_, stroke_element.id)

        if request.form.get('clear'):
            print(f'ClearStroke')
            if stroke_element.piExhaust or stroke_element.prefillTime:
                db.session.delete(stroke_element)
                db.session.commit()
                return redirect(url_for('strokeTime', item_id=item_id, proj_id=proj_id))
            else:
                flash('Calculate before deleting')


    return render_template(html_page, item=getDBElementWithId(itemMaster, int(item_id)), user=current_user,
                           metadata=metadata_, page='strokeTime', valve=valve_element, act=act_element_master,act_case=act_element_case,stroke_element=stroke_element,clearance_vol=clearance_vol,swept_vol=swept_vol)




# Accessories
@app.route('/accessories/proj-<proj_id>/item-<item_id>', methods=['GET', 'POST'])
def accessories(proj_id, item_id):
    item_element = getDBElementWithId(itemMaster, int(item_id))
    valve_element = db.session.query(valveDetailsMaster).filter_by(item=item_element).first()
    accessories_element = db.session.query(accessoriesData).filter_by(item=item_element).first()
    metadata_ = metadata()
    if request.method == 'POST':
        data = request.form.to_dict(flat=False)
        a = jsonify(data).json
        accessories_element.update(a, accessories_element.id)
        return redirect(url_for('accessories', item_id=item_id, proj_id=proj_id))

    return render_template("accessories.html", item=getDBElementWithId(itemMaster, int(item_id)), user=current_user,
                           metadata=metadata_, page='accessories', valve=valve_element, acc=accessories_element)

# Accessories Positioner
@app.route('/positioner/proj-<proj_id>/item-<item_id>', methods=["GET", "POST"])
def positionerRender(proj_id, item_id):
    item_element = getDBElementWithId(itemMaster, int(item_id))
    valve_element = db.session.query(valveDetailsMaster).filter_by(item=item_element).first()
    accessories_element = db.session.query(accessoriesData).filter_by(item=item_element).first()
    positioner_ = positioner.query.all()
    selected_positoner = db.session.query(positioner).filter_by(manufacturer=accessories_element.manufacturer, series=accessories_element.model, action=accessories_element.action).first()
    # print(selected_positoner.id)
    metadata_ = metadata()
    metadata_['positioner'] = positioner_
    return render_template("positioner.html", item=getDBElementWithId(itemMaster, int(item_id)),
                            page='positionerRender', valve=valve_element, metadata=metadata_, 
                            user=current_user, select_pos=selected_positoner)


@app.route('/select-positioner/proj-<proj_id>/item-<item_id>', methods=["GET", "POST"])
def selectPositioner(proj_id, item_id):
    pos_id = request.form.get('positioner')
    pos_element = getDBElementWithId(positioner, pos_id)
    item_element = getDBElementWithId(itemMaster, int(item_id))
    accessories_element = db.session.query(accessoriesData).filter_by(item=item_element).first()
    accessories_element.manufacturer = pos_element.manufacturer
    accessories_element.model = pos_element.series
    accessories_element.action = pos_element.action
    db.session.commit()
    return redirect(url_for('accessories', item_id=item_id, proj_id=proj_id))


# Accessories AFR
@app.route('/afr/proj-<proj_id>/item-<item_id>', methods=["GET", "POST"])
def afrRender(proj_id, item_id):
    item_element = getDBElementWithId(itemMaster, int(item_id))
    valve_element = db.session.query(valveDetailsMaster).filter_by(item=item_element).first()
    afr_ = afr.query.all()
    metadata_ = metadata()
    metadata_['afr_'] = afr_
    return render_template("afr.html", item=getDBElementWithId(itemMaster, int(item_id)),
                            page='positionerRender', valve=valve_element, metadata=metadata_, user=current_user)


@app.route('/select-afr/proj-<proj_id>/item-<item_id>', methods=["GET", "POST"])
def selectAfr(proj_id, item_id):
    afr_id = request.form.get('afr')
    afr_element = getDBElementWithId(afr, afr_id)
    item_element = getDBElementWithId(itemMaster, int(item_id))
    accessories_element = db.session.query(accessoriesData).filter_by(item=item_element).first()
    accessories_element.afr = f"{afr_element.manufacturer}/{afr_element.model}"
    db.session.commit()
    return redirect(url_for('accessories', item_id=item_id, proj_id=proj_id))



# Accessories Limit Switch
@app.route('/limit/proj-<proj_id>/item-<item_id>', methods=["GET", "POST"])
def limitRender(proj_id, item_id):
    item_element = getDBElementWithId(itemMaster, int(item_id))
    valve_element = db.session.query(valveDetailsMaster).filter_by(item=item_element).first()
    limits = limitSwitch.query.all()
    metadata_ = metadata()
    metadata_['limits'] = limits
    return render_template("limitSwitch.html", item=getDBElementWithId(itemMaster, int(item_id)),
                            page='limitRender', valve=valve_element, metadata=metadata_, user=current_user)


@app.route('/select-limit/proj-<proj_id>/item-<item_id>', methods=["GET", "POST"])
def selectlimit(proj_id, item_id):
    limit_id = request.form.get('limit')
    limit_element = getDBElementWithId(limitSwitch, limit_id)
    item_element = getDBElementWithId(itemMaster, int(item_id))
    accessories_element = db.session.query(accessoriesData).filter_by(item=item_element).first()
    accessories_element.limit = limit_element.model
    db.session.commit()
    return redirect(url_for('accessories', item_id=item_id, proj_id=proj_id))


# Accessories Solenoid
@app.route('/solenoid/proj-<proj_id>/item-<item_id>', methods=["GET", "POST"])
def solenoidRender(proj_id, item_id):
    item_element = getDBElementWithId(itemMaster, int(item_id))
    valve_element = db.session.query(valveDetailsMaster).filter_by(item=item_element).first()
    solenoid_ = solenoid.query.all()
    metadata_ = metadata()
    metadata_['solenoid_'] = solenoid_
    return render_template("solenoid.html", item=getDBElementWithId(itemMaster, int(item_id)),
                            page='limitRender', valve=valve_element, metadata=metadata_, user=current_user)


@app.route('/select-solenoid/proj-<proj_id>/item-<item_id>', methods=["GET", "POST"])
def selectSolenoid(proj_id, item_id):
    limit_id = request.form.get('solenoid')
    limit_element = getDBElementWithId(solenoid, limit_id)
    item_element = getDBElementWithId(itemMaster, int(item_id))
    accessories_element = db.session.query(accessoriesData).filter_by(item=item_element).first()
    accessories_element.solenoid_make = limit_element.make
    accessories_element.solenoid_modle = limit_element.model
    accessories_element.solenoid_action = limit_element.type
    db.session.commit()
    return redirect(url_for('accessories', item_id=item_id, proj_id=proj_id))

# Item Notes
@app.route('/item-notes/proj-<proj_id>/item-<item_id>', methods=['GET', 'POST'])
def itemNotes(proj_id, item_id):
    MAX_NOTE_LENGTH = 7
    item_element = getDBElementWithId(itemMaster, int(item_id))
    item_notes_list = db.session.query(itemNotesData).filter_by(item=item_element).order_by('notesNumber').all()
    accessories_element = db.session.query(accessoriesData).filter_by(item=item_element).first()

    uniqueNotes = []
    for notes_ in db.session.query(notesMaster.notesNumber).distinct():
        uniqueNotes.append(notes_.notesNumber)
    
    notes_dict = {}
    for nnn in uniqueNotes:
        contents = db.session.query(notesMaster).filter_by(notesNumber=nnn).all()
        content_list = [cont.content for cont in contents]
        notes_dict[nnn] = content_list
    # print("len of notes comparison")
    # print(len(item_notes_list))
    # print(MAX_NOTE_LENGTH)
    if request.method == 'POST':
        if request.form.get('accessories'):
            
            data = request.form.to_dict(flat=False)
            a = jsonify(data).json
            a.pop('note')
            a.pop('nvalues')
            accessories_element.update(a, accessories_element.id)
        else:
            item_notes_list_2 = db.session.query(itemNotesData).filter_by(item=item_element).order_by('notesNumber').all()
            if len(item_notes_list_2) <= MAX_NOTE_LENGTH:
                note_number = request.form.get('note')
                note_content = request.form.get('nvalues')
                content_list = [abc.content for abc in item_notes_list_2]
                if note_content in content_list:
                    flash(f'Note: "{note_content}" already exists', "error")
                else:
                    print(note_number, note_content)
                    new_item_note = itemNotesData(item=item_element, content=note_content, notesNumber=note_number)
                    db.session.add(new_item_note)
                    db.session.commit()
                    flash("Note Added Successfully", "success")
            else:
                flash(f"Max Length ({MAX_NOTE_LENGTH}) of Notes reached", "error")
        return redirect(url_for('itemNotes', item_id=item_id, proj_id=proj_id))

    return render_template("itemNotes.html", item=getDBElementWithId(itemMaster, int(item_id)), page='itemNotes',
                         user=current_user, dropdown=json.dumps(notes_dict),
                        notes_list=item_notes_list, acc=accessories_element)


# Project Notes
@app.route('/project-notes/proj-<proj_id>/item-<item_id>', methods=['GET', 'POST'])
def project_notes(proj_id, item_id):
    project_element = getDBElementWithId(projectMaster, proj_id)
    notes_ = db.session.query(projectNotes).filter_by(project=project_element).all()
    print(len(notes_))
    if request.method == 'POST':
        new_note = projectNotes(notesNumber=request.form.get('notesNumber'), notes=request.form.get('notes'), project=project_element)
        db.session.add(new_note)
        db.session.commit()
        return redirect(url_for('project_notes', item_id=item_id, proj_id=proj_id, page='project_notes'))

    return render_template("projectNotes.html", item=getDBElementWithId(itemMaster, int(item_id)), user=current_user,
                            page='project_notes', notes=notes_)



@app.route('/del-project-notes/<note_id>/proj-<proj_id>/item-<item_id>', methods=['GET', 'POST'])
def delProjectNotes(note_id, item_id, proj_id):
    note_element = projectNotes.query.get(note_id)
    db.session.delete(note_element)
    db.session.commit()
    # db.session.delete(addresss_element)
    # db.session.commit()
    return redirect(url_for('project_notes',item_id=item_id, proj_id=proj_id))

@app.route('/del-item-notes/<note_id>/proj-<proj_id>/item-<item_id>', methods=['GET', 'POST'])
def delItemNotes(note_id, item_id, proj_id):
    note_element = itemNotesData.query.get(note_id)
    db.session.delete(note_element)
    db.session.commit()
    # db.session.delete(addresss_element)
    # db.session.commit()
    return redirect(url_for('itemNotes',item_id=item_id, proj_id=proj_id))

# Data View Module

@app.route('/view-data/proj-<proj_id>/item-<item_id>', methods=['GET', 'POST'])
def viewData(item_id, proj_id):
    data2 = table_data_render
    metadata_ = metadata()
    return render_template('view_data_old.html', item=getDBElementWithId(itemMaster, int(item_id)), metadata=metadata_, data=data2, page='viewData', user=current_user)


@app.route('/render-data/proj-<proj_id>/item-<item_id>/<topic>', methods=['GET'])
def renderData(topic, item_id, proj_id):
    table_ = table_data_render[int(topic) - 1]['db']
    name = table_data_render[int(topic) - 1]['name']
    all_keys = table_data_render[int(topic) - 1]['db'].__table__.columns.keys()
    all_keys_ = [abc.capitalize() for abc in all_keys]
    table_data = table_.query.all()
    all_data = []
    for data_ in table_data:
        single_row_data = {}
        for key_ in all_keys:
        # all_data[0][all_keys[1]]
            single_row_data[key_] = getattr(data_, key_)
        all_data.append(single_row_data)
    # print(table_.__tablename__)
    # print(len(table_data))
    return render_template("render_data.html", data=table_data, topic=topic, page='renderData', name=name,
                           item=getDBElementWithId(itemMaster, int(item_id)), user=current_user, 
                           all_keys=all_keys, all_data=all_data, all_keys_=all_keys_)


@app.route('/update-data/proj-<proj_id>/item-<item_id>/<topic>/<record_id>', methods=['POST'])
def updateData(topic, item_id, proj_id, record_id):
    table_ = table_data_render[int(topic) - 1]['db']
    data = request.form.to_dict(flat=False)
    a = jsonify(data).json
    a.pop('id')
    record_element = db.session.query(table_).filter_by(id=record_id).first()
    try:
        record_element.update(a, record_element.id)
    except:
        pass
    return redirect(url_for('renderData', topic=topic, item_id=item_id, proj_id=proj_id))




@app.route('/download-data/proj-<proj_id>/item-<item_id>/<topic>', methods=['GET'])
def downloadData(topic, item_id, proj_id):
    table_ = table_data_render[int(topic) - 1]['db']
    name = table_data_render[int(topic) - 1]['name']
    table_data = table_.query.all()
    with open('my_file.csv', 'w', newline='') as csvfile:
        # Create a CSV writer object
        writer = csv.writer(csvfile)

        # Write data to the CSV file
        all_keys = table_data_render[int(topic) - 1]['db'].__table__.columns.keys()
        writer.writerow(all_keys)
        for data_ in table_data:
            single_row_data = []
            for key_ in all_keys:
            # all_data[0][all_keys[1]]
                abc = getattr(data_, key_)
                single_row_data.append(abc)
            writer.writerow(single_row_data)
        # Close the CSV file
        csvfile.close()
    path = 'my_file.csv'
    return send_file(path, as_attachment=True, download_name=f"{table_.__tablename__}.csv")


@app.route('/upload-data/proj-<proj_id>/item-<item_id>/<topic>', methods=['GET', 'POST'])
def uploadData(topic, item_id, proj_id):
    table_ = table_data_render[int(topic) - 1]['db']
    name = table_data_render[int(topic) - 1]['name']
    table_data = table_.query.all()

    if request.method == 'POST':
        try:
            b_list = request.files.get('file').stream.read().decode().strip().split('\n')
            
            all_keys = table_data_render[int(topic) - 1]['db'].__table__.columns.keys()
            table__ = table_data_render[int(topic) - 1]['db']
            others_list = []
            data_delete(table__)
            for i in b_list[1:]:
                i_dict = {}
                for ind in range(len(all_keys[1:])):
                    col_type = table__.__table__.columns[all_keys[1:][ind]].type
                    print(i.split(',')[ind+1])
                    if col_type == String or VARCHAR:
                        i_dict[all_keys[1:][ind]] = str(i.split(',')[ind+1])
                    elif col_type == FLOAT:
                        i_dict[all_keys[1:][ind]] = float(i.split(',')[ind+1])
                    elif col_type == INTEGER:
                        i_dict[all_keys[1:][ind]] = int(i.split(',')[ind+1])
                    # else:
                    #     i_dict[all_keys[ind]] = i.split(',')[ind+1]
                others_list.append(i_dict)
                db.session.add(table__(**i_dict))
                db.session.commit()
            flash('Data Upload Success')
        except Exception as e:
            # Write logic for headers mismatch later
            flash(f'An Error Occured: {e}')
            print(e)



    return redirect(url_for('renderData', topic=topic, item_id=item_id, proj_id=proj_id))



@app.route('/nextItem/<control>/<page>/item-<item_id>/proj-<proj_id>', methods=['GET', 'POST'])
def nextItem(control, page, item_id, proj_id):
    with app.app_context():
        current_item = getDBElementWithId(itemMaster, item_id)
        item_all = db.session.query(itemMaster).filter_by(project=current_item.project).all()
        len_items = len(item_all)
        item_1_index = item_all.index(current_item)
        if control == 'next':
            if item_all.index(current_item)+1 < len_items:
                current_item = db.session.query(itemMaster).filter_by(id=item_all[item_1_index + 1].id).first()
            else:
                current_item = db.session.query(itemMaster).filter_by(id=item_all[-1].id).first()
        elif control == 'prev':
            if item_all.index(current_item) > 0:
                current_item = db.session.query(itemMaster).filter_by(id=item_all[item_1_index - 1].id).first()
            else:
                current_item = db.session.query(itemMaster).filter_by(id=item_all[0].id).first()
        elif control == 'first':
            current_item = db.session.query(itemMaster).filter_by(id=item_all[0].id).first()
            print('condition working')
            print(item_all[0].id)
        elif control == 'last':
            current_item = db.session.query(itemMaster).filter_by(id=item_all[-1].id).first()

        return redirect(url_for(page, item_id=current_item.id, proj_id=current_item.project.id))


@app.route('/generate-csv-item/proj-<proj_id>/item-<item_id>', methods=['GET', 'POST'])
def generate_csv_item(item_id, proj_id):
    valve_element = db.session.query(valveDetailsMaster).filter_by(item=getDBElementWithId(itemMaster, int(item_id))).first()
    if request.method == "POST":
        report_list = request.form.getlist('reportname')
        excel_files = []
        items_list = [item_id]
        for report in report_list:
            if report == 'controlvalve':
                all_items = [getDBElementWithId(itemMaster, i) for i in items_list]
                # all_items = db.session.query(itemMaster).filter_by(project=getDBElementWithId(projectMaster, proj_id)).all()
                
                cases__ = []
                units__ = []
                others__ = []

                for item in all_items:
                    v_details = db.session.query(valveDetailsMaster).filter_by(item=item).first()
                    acc_details = db.session.query(accessoriesData).filter_by(item=item).first()
                    acc_list = [acc_details.manufacturer, acc_details.model, acc_details.action, acc_details.afr,
                                acc_details.afr,
                                acc_details.transmitter, acc_details.limit, acc_details.proximity, acc_details.booster,
                                acc_details.pilot_valve,
                                acc_details.air_lock, acc_details.ip_make, acc_details.ip_model, acc_details.solenoid_make,
                                acc_details.solenoid_model,
                                '3/2 Way', acc_details.volume_tank]
                    # Act data
                    # Act data
                    act_data_string = []
                    # else:
                    act_valve_data_string = []
                    act_other = []
                    act_model = None
                    model_str = None
                    v_model_lower = getValveType(v_details.style.name)
                    

                    # material_ = material_updated.name
                    itemCases_1 = db.session.query(caseMaster).filter_by(item=item).all()
                    date = datetime.date.today().strftime("%d-%m-%Y -- %H-%M-%S")

                    fields___ = ['Flow Rate', 'Inlet Pressure', 'Outlet Pressure', 'Inlet Temperature', 'Specific Gravity',
                                'Viscosity', 'Vapor Pressure', 'Xt', 'Calculated Cv', 'Open %', 'Valve SPL', 'Inlet Velocity',
                                'Outlet Velocity', 'Trim Exit Velocity', 'Tag Number', 'Item Number', 'Fluid State',
                                'Critical Pressure',
                                'Inlet Pipe Size', 'Outlet Pipe Size', 'Valve Size', 'Rating', 'Quote No.', 'Work Order No.',
                                'Customer']

                    rows___ = []

                    # get units
                    cases = db.session.query(caseMaster).filter_by(item=item).all()
                    if len(cases) == 0:
                        pass
                    else:
                        last_case = cases[len(cases) - 1]
                        
                        if v_model_lower == 'globe':
                            percent__, i_pipe_vel, o_pipe_vel, t_vel = '%', 'm/s', 'm/s', 'm/s'
                        else:
                            percent__, i_pipe_vel, o_pipe_vel, t_vel = 'degree', 'mach', 'mach', 'mach'
                        unit_list = [item.project.flowrateUnit, item.project.pressureUnit, item.project.pressureUnit, item.project.temperatureUnit, '', 'centipose', item.project.pressureUnit, '', '', percent__,
                                    'dB',
                                    i_pipe_vel,
                                    o_pipe_vel, t_vel, item.project.lengthUnit, item.project.lengthUnit]
                        
                    

                        item_notes_list = db.session.query(itemNotesData).filter_by(item=item).order_by('notesNumber').all()

                        cv_value_element = db.session.query(cvValues).filter_by(cv=cases[0].cv).first()
                        try:
                            spec_fluid_name = cases[0].fluid.fluidName
                        except:
                            spec_fluid_name = None
                        if not cv_value_element:
                            seat_bore = None
                            travel_ = None
                        else:
                            seat_bore = cv_value_element.seatBore
                            travel_ = cv_value_element.travel

                        other_val_list = [v_details.serialNumber, 1, item.project.projectRef, cases[0].criticalPressure, item.project.pressureUnit, v_details.shutOffDelP, cases[0].valveSize, item.project.lengthUnit, v_details.rating.name,
                                        v_details.material.name, v_details.bonnetType__.name, "See Note 1", "See Note 1", v_details.gasket__.name, v_details.trimType__.name, v_details.flowDirection__.name, v_details.seat__.name,
                                        v_details.disc__.name,
                                        v_details.seatLeakageClass__.name, v_details.endConnection__.name, v_details.endFinish__.name, v_model_lower, model_str, v_details.bonnet__.name,
                                        v_details.bonnetExtDimension, v_details.studNut__.name, cases[0].ratedCv, v_details.balanceSeal__.name, acc_list, v_details.application, spec_fluid_name, 
                                        v_details.maxPressure, v_details.maxTemp, v_details.minTemp, None, None, v_details.packing__.name,
                                        seat_bore, travel_, v_details.flowDirection__.name, v_details.flowCharacter__.name, v_details.shaft__.name, item_notes_list]
                        
                        customer__ = db.session.query(addressProject).filter_by(isCompany=True, project=item.project).first()
                        
                        for i in itemCases_1[:6]:
                            case_list = [i.flowrate, i.inletPressure, i.outletPressure, i.inletTemp, i.specificGravity, i.kinematicViscosity, i.vaporPressure,
                                        i.xt,
                                        i.calculatedCv, i.openingPercentage, i.spl,
                                        i.pipeInVel, i.pipeOutVel, i.tex, v_details.tagNumber, item.id,
                                        v_details.state.name, itemCases_1[0].criticalPressure,
                                        itemCases_1[0].inletPipeSize, itemCases_1[0].outletPipeSize, i.valveSize, v_details.rating.name, item.project.projectId,
                                        item.project.workOderNo,
                                        f"{customer__.address.company.name} {customer__.address.address}"]
                            
                            # case_list_dict = {
                            #                     "flowrate": i.flowrate, "iPressure": i.iPressure, "oPressure": i.oPressure,
                            #                     "iTemp": i.iTemp, "sGravity": i.sGravity, "viscosity": i.viscosity, "vPressure": i.vPressure,
                            #                     "Xt": i.Xt, "CV": i.CV, "openPercent": i.openPercent, "valveSPL": i.valveSPL,
                            #                     "iVelocity": i.iVelocity, "oVelocity": i.oVelocity, "trimExVelocity": i.trimExVelocity, "tagNo": item.tag_no,
                            #                     "itemId": item.id, "fluidState": itemCases_1[0].fluidState, "criticalPressure": itemCases_1[0].criticalPressure,
                            #                     "iPipeSize": itemCases_1[0].iPipeSize, "oPipeSize": itemCases_1[0].oPipeSize, "size_": size__, "rating": rating__,
                            #                     "quote": project__.quote, "workOrder": project__.work_order, "customer": customer__
                            #                 }
                            rows___.append(case_list)

                        cases__.append(rows___)
                        units__.append(unit_list)
                        others__.append(other_val_list)
                        try:
                            act_dict_ = {'v_type': cases[0].ratedCv, 'trim_type': v_details.trimType__.name, 'Balancing': v_details.balanceSeal__.name,
                                        'fl_direction': v_details.flowDirection__.name, 'v_size': cases[0].valveSize,
                                        'v_size_unit': item.project.lengthUnit,
                                        'Seat_Dia': i.seatDia,
                                        'seat_dia_unit': item.project.lengthUnit, 'unbalance_area': act_valve_data_string[5],
                                        'unbalance_area_unit': 'inch^2',
                                        'Stem_size': act_valve_data_string[4], 'Stem_size_unit': 'inch',
                                        'Travel': act_valve_data_string[1],
                                        'travel_unit': 'inch', 'Packing_Friction': act_data_string[13],
                                        'packing_friction_unit': 'mm', 'Seat_Load_Factor': act_data_string[24],
                                        'Additional_Factor': 0,
                                        'P1': itemCases_1[-1].iPressure,
                                        'p1_unit': item.project.pressureUnit,
                                        'P2': itemCases_1[-1].oPressure, 'p2_unit': item.project.pressureUnit,
                                        'delP_Shutoff': v_details.shutOffDelP, 'delP_Shutoff_unit': 'bar', 'unbal_force': 0,
                                        'Kn': act_data_string[15], 'delP_flowing': 0,
                                        'act_type': act_other[0],
                                        'fail_action': act_data_string[4], 'act_size': act_data_string[0],
                                        'act_size_unit': 'inch',
                                        'act_travel': act_data_string[1], 'act_travel_unit': 'inch',
                                        'eff_area': act_data_string[0], 'eff_area_unit': 'inch^2',
                                        'sMin': act_data_string[2], 'sMax': act_data_string[3], 'spring_rate': act_data_string[18],
                                        'spring_windup': act_data_string[19], 'max_spring_load': act_data_string[20],
                                        'max_air_supply': act_other[6],
                                        'set_pressure': act_data_string[5], 'set_pressure_unit': 'bar', 'act_thrust_down': 0,
                                        'act_thrust_up': 0, 'handwheel': act_other[2],
                                        'friction_band': act_data_string[21],
                                        'req_handWheel_thrust': act_data_string[22], 'max_thrust': act_data_string[23],
                                        'v_thrust_close': 0, 'v_thrust_open': 0, 'seat_load': act_data_string[14],
                                        'orientation': act_other[3], 'act_model': act_model, 'travel_stops': act_other[8]
                                        }
                        except IndexError:
                            act_dict_ = {'v_type': cases[0].ratedCv, 'trim_type': v_details.trimType__.name, 'Balancing': v_details.balanceSeal__.name,
                                        'fl_direction':  v_details.flowDirection__.name, 'v_size': cases[0].valveSize,
                                        'v_size_unit': item.project.lengthUnit,
                                        'Seat_Dia': i.seatDia,
                                        'seat_dia_unit': item.project.lengthUnit, 'unbalance_area': None,
                                        'unbalance_area_unit': 'inch^2',
                                        'Stem_size': None, 'Stem_size_unit': 'inch',
                                        'Travel': None,
                                        'travel_unit': 'inch', 'Packing_Friction': None,
                                        'packing_friction_unit': 'mm', 'Seat_Load_Factor': None,
                                        'Additional_Factor': 0,
                                        'P1': itemCases_1[-1].inletPressure,
                                        'p1_unit': item.project.pressureUnit,
                                        'P2': itemCases_1[-1].outletPressure, 'p2_unit': item.project.pressureUnit,
                                        'delP_Shutoff': v_details.shutOffDelP, 'delP_Shutoff_unit': 'bar', 'unbal_force': 0,
                                        'Kn': None, 'delP_flowing': 0,
                                        'act_type': None,
                                        'fail_action': None, 'act_size': None,
                                        'act_size_unit': 'inch',
                                        'act_travel': None, 'act_travel_unit': 'inch',
                                        'eff_area': None, 'eff_area_unit': 'inch^2',
                                        'sMin': None, 'sMax': None, 'spring_rate': None,
                                        'spring_windup': None, 'max_spring_load': None,
                                        'max_air_supply': None,
                                        'set_pressure': None, 'set_pressure_unit': 'bar', 'act_thrust_down': 0,
                                        'act_thrust_up': 0, 'handwheel': None,
                                        'friction_band': None,
                                        'req_handWheel_thrust': None, 'max_thrust': None,
                                        'v_thrust_close': 0, 'v_thrust_open': 0, 'seat_load': None,
                                        'orientation': None, 'act_model': act_model, 'travel_stops': None
                                        }
                        act_dict = act_dict_

                print(act_dict)
                createSpecSheet(cases__, units__, others__, act_dict)
                path = "specsheet.xlsx"
                project_number = item.project.id
                current_datetime = datetime.datetime.today().date().timetuple()

                str_current_datetime = str(current_datetime)
                a__ = datetime.datetime.now()
                a_ = a__.strftime("%a, %d %b %Y %H-%M-%S")
                spec_sheet_name = f'ControlValveSpecification{project_number}_{a_}.xlsx' 
            
                excel_files.append((path,spec_sheet_name))
            

            elif report == 'cvplot':
                # items_ids_list = [int(x) for x in item_ids.strip('[]').split(',')]
                items = [getDBElementWithId(itemMaster, i) for i in items_list]
                print(f'generate_openingcvssss {items}')
                #valveDetails = db.session.query(valveDetailsMaster).filter_by(item=item).first()
                itemCase = [db.session.query(caseMaster).filter_by(item=item).all() for item in items]
                
                valve_element = [db.session.query(valveDetailsMaster).filter_by(item=item).first() for item in items]
                fluid_types = [fluid.state.name for fluid in valve_element]
                project_element = getDBElementWithId(projectMaster,proj_id)
                customer__ = db.session.query(addressProject).filter_by(isCompany=True, project=project_element).first()
                enduser__ = db.session.query(addressProject).filter_by(isCompany=False, project=project_element).first()
                header_details = []
                for valve in valve_element:
                    # critical_pres = itemCase[valve_element.index(valve)][0].criticalPressure
                    critical_pres = 220
                    critical_pres_unit = "bar (g)"
                    # critical_pres_unit = items[valve_element.index(valve)].criticalpres_unit
                    header = [f"{customer__.address.company.name} {customer__.address.address}",
                               project_element.projectRef,
                               f"{enduser__.address.company.name} {enduser__.address.address}",
                               project_element.enquiryRef, 
                               project_element.custPoNo,
                               project_element.projectId,
                               project_element.workOderNo,
                               valve.serialNumber, 
                               valve.tagNumber, 
                               valve.quantity, 
                               valve.application, 
                               f"{valve.state.name} / ",
                               f"{critical_pres} / {critical_pres_unit}",
                               f"{valve.shutOffDelP} / {valve.shutOffDelPUnit}"
                               ]
                    header_details.append(header)


                # header_details = [f"{customer__.address.company.name} {customer__.address.address}",f"{enduser__.address.company.name} {enduser__.address.address}"]  

                    

                createcvOpening_gas(itemCase,fluid_types,items,header_details)


                path = "specsheet1.xlsx"
                a__ = datetime.datetime.now()
                a_ = a__.strftime("%a, %d %b %Y %H-%M-%S")
                spec_sheet_name = f'CVPlot_{a_}.xlsx'
                excel_files.append((path,spec_sheet_name))
        

        files_excel = []
        for file in excel_files:
            files_excel.append(file[0])
        
        print(f'EXCELFILE {files_excel}')
        # Create a zip file containing all Excel files
        zip_file_path = os.path.join(r'E:\Reports', 'item_reports')
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            for file in files_excel:
                zipf.write(file, os.path.basename(file))

        # Provide the zip file for download
        if len(files_excel) == 1:
            print(f'PPPPPPPPPPPPPPPPPPP {files_excel[0]}')
            report_sheet = {'specsheet.xlsx':'ControlValveSizingSheetItem.xlsx', 'specsheet1.xlsx':'CVPlotItem.xlsx'}
            return send_file(files_excel[0], as_attachment=True, download_name=report_sheet[files_excel[0]])
        else:
            return send_file(zip_file_path, as_attachment=True)
    
    return render_template('item_print.html', valve=valve_element, item=getDBElementWithId(itemMaster, int(item_id)), page='generate_csv_item', user=current_user)

@app.route('/generate_openingcv/proj-<proj_id>/item-<item_ids>',methods=['GET','POST'])
def generate_openingcv(item_ids,proj_id):
    items_ids_list = [int(x) for x in item_ids.strip('[]').split(',')]
    items = [getDBElementWithId(itemMaster, i) for i in items_ids_list]
    print(f'generate_openingcvssss {items}')
    #valveDetails = db.session.query(valveDetailsMaster).filter_by(item=item).first()
    itemCase = [db.session.query(caseMaster).filter_by(item=item).all() for item in items]
    valve_element = [db.session.query(valveDetailsMaster).filter_by(item=item).first() for item in items]
    fluid_types = [fluid.state.name for fluid in valve_element]
    project_element = getDBElementWithId(projectMaster,proj_id)
    
    customer__ = db.session.query(addressProject).filter_by(isCompany=True, project=project_element).first()
    header_details = [f"{customer__.address.company.name} {customer__.address.address}"]  

    createcvOpening_gas(itemCase,fluid_types,items,header_details)


    path = "specsheet1.xlsx"
    a__ = datetime.datetime.now()
    a_ = a__.strftime("%a, %d %b %Y %H-%M-%S")
    spec_sheet_name = f'CVPlot_{a_}.xlsx'

    return send_file(path, as_attachment=True, download_name=spec_sheet_name)

# def generateallreports(excel_files):
#     print(f'ALL REPORTS {excel_files}')
#     # Create a zip file containing all Excel files
#     with zipfile.ZipFile('excel_files.zip', 'w') as zipf:
#         for file in excel_files:
#             zipf.write(file, os.path.basename(file))

#     # Provide the zip file for download
#     return send_file('excel_files.zip', as_attachment=True)



@app.route('/generate-csv-project/proj-<proj_id>/item-<item_id>', methods=['GET', 'POST'])
def generate_csv_project(item_id, proj_id):
    items_list = db.session.query(itemMaster).filter_by(project=projectMaster.query.get(int(proj_id))).order_by(
        itemMaster.itemNumber.asc()).all()
    valve_list = [db.session.query(valveDetailsMaster).filter_by(item=item_).first() for item_ in items_list]
    if request.method == "POST":
        items = request.form.getlist('item')
        items_list = [int(i) for i in items]
        report_list = request.form.getlist('reportname')
        print(f'JJSHSFORM {report_list},{items}')
        excel_files = []
      
            

        for report in report_list:
            
            if report == 'controlvalve':
                # items_ids_list = [int(x) for x in item_id.strip('[]').split(',')]
                all_items = [getDBElementWithId(itemMaster, i) for i in items_list]
                # all_items = db.session.query(itemMaster).filter_by(project=getDBElementWithId(projectMaster, proj_id)).all()
                
                cases__ = []
                units__ = []
                others__ = []

                for item in all_items:
                    v_details = db.session.query(valveDetailsMaster).filter_by(item=item).first()
                    acc_details = db.session.query(accessoriesData).filter_by(item=item).first()
                    acc_list = [acc_details.manufacturer, acc_details.model, acc_details.action, acc_details.afr,
                                acc_details.afr,
                                acc_details.transmitter, acc_details.limit, acc_details.proximity, acc_details.booster,
                                acc_details.pilot_valve,
                                acc_details.air_lock, acc_details.ip_make, acc_details.ip_model, acc_details.solenoid_make,
                                acc_details.solenoid_model,
                                '3/2 Way', acc_details.volume_tank]
                    # Act data
                    # Act data
                    act_data_string = []
                    # else:
                    act_valve_data_string = []
                    act_other = []
                    act_model = None
                    model_str = None
                    v_model_lower = getValveType(v_details.style.name)
                    

                    # material_ = material_updated.name
                    itemCases_1 = db.session.query(caseMaster).filter_by(item=item).all()
                    date = datetime.date.today().strftime("%d-%m-%Y -- %H-%M-%S")

                    fields___ = ['Flow Rate', 'Inlet Pressure', 'Outlet Pressure', 'Inlet Temperature', 'Specific Gravity',
                                'Viscosity', 'Vapor Pressure', 'Xt', 'Calculated Cv', 'Open %', 'Valve SPL', 'Inlet Velocity',
                                'Outlet Velocity', 'Trim Exit Velocity', 'Tag Number', 'Item Number', 'Fluid State',
                                'Critical Pressure',
                                'Inlet Pipe Size', 'Outlet Pipe Size', 'Valve Size', 'Rating', 'Quote No.', 'Work Order No.',
                                'Customer']

                    rows___ = []

                    # get units
                    cases = db.session.query(caseMaster).filter_by(item=item).all()
                    if len(cases) == 0:
                        pass
                    else:
                        last_case = cases[len(cases) - 1]
                        
                        if v_model_lower == 'globe':
                            percent__, i_pipe_vel, o_pipe_vel, t_vel = '%', 'm/s', 'm/s', 'm/s'
                        else:
                            percent__, i_pipe_vel, o_pipe_vel, t_vel = 'degree', 'mach', 'mach', 'mach'
                        unit_list = [item.project.flowrateUnit, item.project.pressureUnit, item.project.pressureUnit, item.project.temperatureUnit, '', 'centipose', item.project.pressureUnit, '', '', percent__,
                                    'dB',
                                    i_pipe_vel,
                                    o_pipe_vel, t_vel, item.project.lengthUnit, item.project.lengthUnit]
                        
                    

                        item_notes_list = db.session.query(itemNotesData).filter_by(item=item).order_by('notesNumber').all()

                        cv_value_element = db.session.query(cvValues).filter_by(cv=cases[0].cv).first()
                        try:
                            spec_fluid_name = cases[0].fluid.fluidName
                        except:
                            spec_fluid_name = None
                        if not cv_value_element:
                            seat_bore = None
                            travel_ = None
                        else:
                            seat_bore = cv_value_element.seatBore
                            travel_ = cv_value_element.travel

                        other_val_list = [v_details.serialNumber, 1, item.project.projectRef, cases[0].criticalPressure, item.project.pressureUnit, v_details.shutOffDelP, cases[0].valveSize, item.project.lengthUnit, v_details.rating.name,
                                        v_details.material.name, v_details.bonnetType__.name, "See Note 1", "See Note 1", v_details.gasket__.name, v_details.trimType__.name, v_details.flowDirection__.name, v_details.seat__.name,
                                        v_details.disc__.name,
                                        v_details.seatLeakageClass__.name, v_details.endConnection__.name, v_details.endFinish__.name, v_model_lower, model_str, v_details.bonnet__.name,
                                        v_details.bonnetExtDimension, v_details.studNut__.name, cases[0].ratedCv, v_details.balanceSeal__.name, acc_list, v_details.application, spec_fluid_name, 
                                        v_details.maxPressure, v_details.maxTemp, v_details.minTemp, None, None, v_details.packing__.name,
                                        seat_bore, travel_, v_details.flowDirection__.name, v_details.flowCharacter__.name, v_details.shaft__.name, item_notes_list]
                        
                        customer__ = db.session.query(addressProject).filter_by(isCompany=True, project=item.project).first()
                        
                        for i in itemCases_1[:6]:
                            case_list = [i.flowrate, i.inletPressure, i.outletPressure, i.inletTemp, i.specificGravity, i.kinematicViscosity, i.vaporPressure,
                                        i.xt,
                                        i.calculatedCv, i.openingPercentage, i.spl,
                                        i.pipeInVel, i.pipeOutVel, i.tex, v_details.tagNumber, item.id,
                                        v_details.state.name, itemCases_1[0].criticalPressure,
                                        itemCases_1[0].inletPipeSize, itemCases_1[0].outletPipeSize, i.valveSize, v_details.rating.name, item.project.projectId,
                                        item.project.workOderNo,
                                        f"{customer__.address.company.name} {customer__.address.address}"]
                            
                            # case_list_dict = {
                            #                     "flowrate": i.flowrate, "iPressure": i.iPressure, "oPressure": i.oPressure,
                            #                     "iTemp": i.iTemp, "sGravity": i.sGravity, "viscosity": i.viscosity, "vPressure": i.vPressure,
                            #                     "Xt": i.Xt, "CV": i.CV, "openPercent": i.openPercent, "valveSPL": i.valveSPL,
                            #                     "iVelocity": i.iVelocity, "oVelocity": i.oVelocity, "trimExVelocity": i.trimExVelocity, "tagNo": item.tag_no,
                            #                     "itemId": item.id, "fluidState": itemCases_1[0].fluidState, "criticalPressure": itemCases_1[0].criticalPressure,
                            #                     "iPipeSize": itemCases_1[0].iPipeSize, "oPipeSize": itemCases_1[0].oPipeSize, "size_": size__, "rating": rating__,
                            #                     "quote": project__.quote, "workOrder": project__.work_order, "customer": customer__
                            #                 }
                            rows___.append(case_list)

                        cases__.append(rows___)
                        units__.append(unit_list)
                        others__.append(other_val_list)
                        try:
                            act_dict_ = {'v_type': cases[0].ratedCv, 'trim_type': v_details.trimType__.name, 'Balancing': v_details.balanceSeal__.name,
                                        'fl_direction': v_details.flowDirection__.name, 'v_size': cases[0].valveSize,
                                        'v_size_unit': item.project.lengthUnit,
                                        'Seat_Dia': i.seatDia,
                                        'seat_dia_unit': item.project.lengthUnit, 'unbalance_area': act_valve_data_string[5],
                                        'unbalance_area_unit': 'inch^2',
                                        'Stem_size': act_valve_data_string[4], 'Stem_size_unit': 'inch',
                                        'Travel': act_valve_data_string[1],
                                        'travel_unit': 'inch', 'Packing_Friction': act_data_string[13],
                                        'packing_friction_unit': 'mm', 'Seat_Load_Factor': act_data_string[24],
                                        'Additional_Factor': 0,
                                        'P1': itemCases_1[-1].iPressure,
                                        'p1_unit': item.project.pressureUnit,
                                        'P2': itemCases_1[-1].oPressure, 'p2_unit': item.project.pressureUnit,
                                        'delP_Shutoff': v_details.shutOffDelP, 'delP_Shutoff_unit': 'bar', 'unbal_force': 0,
                                        'Kn': act_data_string[15], 'delP_flowing': 0,
                                        'act_type': act_other[0],
                                        'fail_action': act_data_string[4], 'act_size': act_data_string[0],
                                        'act_size_unit': 'inch',
                                        'act_travel': act_data_string[1], 'act_travel_unit': 'inch',
                                        'eff_area': act_data_string[0], 'eff_area_unit': 'inch^2',
                                        'sMin': act_data_string[2], 'sMax': act_data_string[3], 'spring_rate': act_data_string[18],
                                        'spring_windup': act_data_string[19], 'max_spring_load': act_data_string[20],
                                        'max_air_supply': act_other[6],
                                        'set_pressure': act_data_string[5], 'set_pressure_unit': 'bar', 'act_thrust_down': 0,
                                        'act_thrust_up': 0, 'handwheel': act_other[2],
                                        'friction_band': act_data_string[21],
                                        'req_handWheel_thrust': act_data_string[22], 'max_thrust': act_data_string[23],
                                        'v_thrust_close': 0, 'v_thrust_open': 0, 'seat_load': act_data_string[14],
                                        'orientation': act_other[3], 'act_model': act_model, 'travel_stops': act_other[8]
                                        }
                        except IndexError:
                            act_dict_ = {'v_type': cases[0].ratedCv, 'trim_type': v_details.trimType__.name, 'Balancing': v_details.balanceSeal__.name,
                                        'fl_direction':  v_details.flowDirection__.name, 'v_size': cases[0].valveSize,
                                        'v_size_unit': item.project.lengthUnit,
                                        'Seat_Dia': i.seatDia,
                                        'seat_dia_unit': item.project.lengthUnit, 'unbalance_area': None,
                                        'unbalance_area_unit': 'inch^2',
                                        'Stem_size': None, 'Stem_size_unit': 'inch',
                                        'Travel': None,
                                        'travel_unit': 'inch', 'Packing_Friction': None,
                                        'packing_friction_unit': 'mm', 'Seat_Load_Factor': None,
                                        'Additional_Factor': 0,
                                        'P1': itemCases_1[-1].inletPressure,
                                        'p1_unit': item.project.pressureUnit,
                                        'P2': itemCases_1[-1].outletPressure, 'p2_unit': item.project.pressureUnit,
                                        'delP_Shutoff': v_details.shutOffDelP, 'delP_Shutoff_unit': 'bar', 'unbal_force': 0,
                                        'Kn': None, 'delP_flowing': 0,
                                        'act_type': None,
                                        'fail_action': None, 'act_size': None,
                                        'act_size_unit': 'inch',
                                        'act_travel': None, 'act_travel_unit': 'inch',
                                        'eff_area': None, 'eff_area_unit': 'inch^2',
                                        'sMin': None, 'sMax': None, 'spring_rate': None,
                                        'spring_windup': None, 'max_spring_load': None,
                                        'max_air_supply': None,
                                        'set_pressure': None, 'set_pressure_unit': 'bar', 'act_thrust_down': 0,
                                        'act_thrust_up': 0, 'handwheel': None,
                                        'friction_band': None,
                                        'req_handWheel_thrust': None, 'max_thrust': None,
                                        'v_thrust_close': 0, 'v_thrust_open': 0, 'seat_load': None,
                                        'orientation': None, 'act_model': act_model, 'travel_stops': None
                                        }
                        act_dict = act_dict_

                print(act_dict)
                createSpecSheet(cases__, units__, others__, act_dict)
                path = "specsheet.xlsx"
                project_number = item.project.id
                current_datetime = datetime.datetime.today().date().timetuple()

                str_current_datetime = str(current_datetime)
                a__ = datetime.datetime.now()
                a_ = a__.strftime("%a, %d %b %Y %H-%M-%S")
                spec_sheet_name = f'ControlValveSpecification{project_number}_{a_}.xlsx' 
                excel_files.append((path,spec_sheet_name))
            
            elif report == 'cvplot':
                # items_ids_list = [int(x) for x in item_ids.strip('[]').split(',')]
                items = [getDBElementWithId(itemMaster, i) for i in items_list]
                print(f'generate_openingcvssss {items}')
                #valveDetails = db.session.query(valveDetailsMaster).filter_by(item=item).first()
                itemCase = [db.session.query(caseMaster).filter_by(item=item).all() for item in items]
                
                valve_element = [db.session.query(valveDetailsMaster).filter_by(item=item).first() for item in items]
                fluid_types = [fluid.state.name for fluid in valve_element]
                project_element = getDBElementWithId(projectMaster,proj_id)
                customer__ = db.session.query(addressProject).filter_by(isCompany=True, project=project_element).first()
                enduser__ = db.session.query(addressProject).filter_by(isCompany=False, project=project_element).first()
                header_details = []
                for valve in valve_element:
                    # critical_pres = itemCase[valve_element.index(valve)][0].criticalPressure
                    critical_pres = 220
                    critical_pres_unit = "bar (g)"
                    # critical_pres_unit = items[valve_element.index(valve)].criticalpres_unit
                    header = [f"{customer__.address.company.name} {customer__.address.address}",
                               project_element.projectRef,
                               f"{enduser__.address.company.name} {enduser__.address.address}",
                               project_element.enquiryRef, 
                               project_element.custPoNo,
                               project_element.projectId,
                               project_element.workOderNo,
                               valve.serialNumber, 
                               valve.tagNumber, 
                               valve.quantity, 
                               valve.application, 
                               f"{valve.state.name} / ",
                               f"{critical_pres} / {critical_pres_unit}",
                               f"{valve.shutOffDelP} / {valve.shutOffDelPUnit}"
                               ]
                    header_details.append(header)


                # header_details = [f"{customer__.address.company.name} {customer__.address.address}",f"{enduser__.address.company.name} {enduser__.address.address}"]  

                    

                createcvOpening_gas(itemCase,fluid_types,items,header_details)


                path = "specsheet1.xlsx"
                a__ = datetime.datetime.now()
                a_ = a__.strftime("%a, %d %b %Y %H-%M-%S")
                spec_sheet_name = f'CVPlot_{a_}.xlsx'
                excel_files.append((path,spec_sheet_name))
        
            elif report == 'actuatorsizing':
                createActSpecSheet()

                path = "act_specsheet.xlsx"
                a__ = datetime.datetime.now()
                a_ = a__.strftime("%a, %d %b %Y %H-%M-%S")
                spec_sheet_name = f'ActuatorSizing_{a_}.xlsx'
                excel_files.append((path,spec_sheet_name))

        files_excel = []
        for file in excel_files:
            files_excel.append(file[0])
        
        print(f'EXCELFILE {files_excel}')
        # Create a zip file containing all Excel files
        zip_file_path = os.path.join(r'E:\Reports', 'project_reports')
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            for file in files_excel:
                zipf.write(file, os.path.basename(file))

       
        if len(files_excel) == 1:
            print(f'PPPPPPPPPPPPPPPPPPP {files_excel[0]}')
            report_sheet = {'specsheet.xlsx':'ControlValveSizingSheet.xlsx', 'specsheet1.xlsx':'CVPlot.xlsx','act_specsheet.xlsx':'ActuatorSizingSheet.xlsx'}
            return send_file(files_excel[0], as_attachment=True, download_name=report_sheet[files_excel[0]])
        else:
            return send_file('excel_files.zip', as_attachment=True)





        # if 'controlvalve' in request.form:
        #     print('yes')
        #     return redirect(url_for('generate_csv', item_id=items_list, proj_id=proj_id, page='generate_csv_project'))
        # elif 'cvplot' in request.form:
        #     return redirect(url_for('generate_openingcv',item_ids=items_list, proj_id=proj_id))
        
    return render_template('project_print.html', items=valve_list, item=getDBElementWithId(itemMaster, int(item_id)), page='generate_csv_project', user=current_user)


@app.route('/generate-csv/proj-<proj_id>/item-<item_id>/<page>', methods=['GET', 'POST'])
def generate_csv(item_id, proj_id, page):
    try:
        with app.app_context():
            # item_selected = getDBElementWithId(itemMaster, item_id)
            # project_ = item_selected.project
            items_ids_list = [int(x) for x in item_id.strip('[]').split(',')]
            all_items = [getDBElementWithId(itemMaster, i) for i in items_ids_list]
            # all_items = db.session.query(itemMaster).filter_by(project=getDBElementWithId(projectMaster, proj_id)).all()
            
            cases__ = []
            units__ = []
            others__ = []

            for item in all_items:
                v_details = db.session.query(valveDetailsMaster).filter_by(item=item).first()
                acc_details = db.session.query(accessoriesData).filter_by(item=item).first()
                acc_list = [acc_details.manufacturer, acc_details.model, acc_details.action, acc_details.afr,
                            acc_details.afr,
                            acc_details.transmitter, acc_details.limit, acc_details.proximity, acc_details.booster,
                            acc_details.pilot_valve,
                            acc_details.air_lock, acc_details.ip_make, acc_details.ip_model, acc_details.solenoid_make,
                            acc_details.solenoid_model,
                            '3/2 Way', acc_details.volume_tank]
                # Act data
                # Act data
                act_data_string = []
                # else:
                act_valve_data_string = []
                act_other = []
                act_model = None
                model_str = None
                v_model_lower = getValveType(v_details.style.name)
                

                # material_ = material_updated.name
                itemCases_1 = db.session.query(caseMaster).filter_by(item=item).all()
                date = datetime.date.today().strftime("%d-%m-%Y -- %H-%M-%S")

                fields___ = ['Flow Rate', 'Inlet Pressure', 'Outlet Pressure', 'Inlet Temperature', 'Specific Gravity',
                            'Viscosity', 'Vapor Pressure', 'Xt', 'Calculated Cv', 'Open %', 'Valve SPL', 'Inlet Velocity',
                            'Outlet Velocity', 'Trim Exit Velocity', 'Tag Number', 'Item Number', 'Fluid State',
                            'Critical Pressure',
                            'Inlet Pipe Size', 'Outlet Pipe Size', 'Valve Size', 'Rating', 'Quote No.', 'Work Order No.',
                            'Customer']

                rows___ = []

                # get units
                cases = db.session.query(caseMaster).filter_by(item=item).all()
                if len(cases) == 0:
                    pass
                else:
                    last_case = cases[len(cases) - 1]
                    
                    if v_model_lower == 'globe':
                        percent__, i_pipe_vel, o_pipe_vel, t_vel = '%', 'm/s', 'm/s', 'm/s'
                    else:
                        percent__, i_pipe_vel, o_pipe_vel, t_vel = 'degree', 'mach', 'mach', 'mach'
                    unit_list = [item.flowrate_unit, item.inpres_unit, item.outpres_unit, item.intemp_unit, '', 'centipose', item.project.pressureUnit, '', '', percent__,
                                'dB',
                                i_pipe_vel,
                                o_pipe_vel, t_vel, item.inpipe_unit, item.outpipe_unit]
                    
                

                    item_notes_list = db.session.query(itemNotesData).filter_by(item=item).order_by('notesNumber').all()

                    cv_value_element = db.session.query(cvValues).filter_by(cv=cases[0].cv).first()
                    try:
                        spec_fluid_name = cases[0].fluid.fluidName
                    except:
                        spec_fluid_name = None
                    if not cv_value_element:
                        seat_bore = None
                        travel_ = None
                    else:
                        seat_bore = cv_value_element.seatBore
                        travel_ = cv_value_element.travel

                    other_val_list = [v_details.serialNumber, 1, item.project.projectRef, cases[0].criticalPressure, item.criticalpres_unit, v_details.shutOffDelP, cases[0].valveSize, item.valvesize_unit, v_details.rating.name,
                                    v_details.material.name, v_details.bonnetType__.name, "See Note 1", "See Note 1", v_details.gasket__.name, v_details.trimType__.name, v_details.flowDirection__.name, v_details.seat__.name,
                                    v_details.disc__.name,
                                    v_details.seatLeakageClass__.name, v_details.endConnection__.name, v_details.endFinish__.name, v_model_lower, model_str, v_details.bonnet__.name,
                                    v_details.bonnetExtDimension, v_details.studNut__.name, cases[0].ratedCv, v_details.balanceSeal__.name, acc_list, v_details.application, spec_fluid_name, 
                                    v_details.maxPressure, v_details.maxTemp, v_details.minTemp, None, None, v_details.packing__.name,
                                    seat_bore, travel_, v_details.flowDirection__.name, v_details.flowCharacter__.name, v_details.shaft__.name, item_notes_list]
                    
                    customer__ = db.session.query(addressProject).filter_by(isCompany=True, project=item.project).first()
                    
                    for i in itemCases_1[:6]:
                        case_list = [i.flowrate, i.inletPressure, i.outletPressure, i.inletTemp, i.specificGravity, i.kinematicViscosity, i.vaporPressure,
                                    i.xt,
                                    i.calculatedCv, i.openingPercentage, i.spl,
                                    i.pipeInVel, i.pipeOutVel, i.tex, v_details.tagNumber, item.id,
                                    v_details.state.name, itemCases_1[0].criticalPressure,
                                    itemCases_1[0].inletPipeSize, itemCases_1[0].outletPipeSize, i.valveSize, v_details.rating.name, item.project.projectId,
                                    item.project.workOderNo,
                                    f"{customer__.address.company.name} {customer__.address.address}"]
                        
                        # case_list_dict = {
                        #                     "flowrate": i.flowrate, "iPressure": i.iPressure, "oPressure": i.oPressure,
                        #                     "iTemp": i.iTemp, "sGravity": i.sGravity, "viscosity": i.viscosity, "vPressure": i.vPressure,
                        #                     "Xt": i.Xt, "CV": i.CV, "openPercent": i.openPercent, "valveSPL": i.valveSPL,
                        #                     "iVelocity": i.iVelocity, "oVelocity": i.oVelocity, "trimExVelocity": i.trimExVelocity, "tagNo": item.tag_no,
                        #                     "itemId": item.id, "fluidState": itemCases_1[0].fluidState, "criticalPressure": itemCases_1[0].criticalPressure,
                        #                     "iPipeSize": itemCases_1[0].iPipeSize, "oPipeSize": itemCases_1[0].oPipeSize, "size_": size__, "rating": rating__,
                        #                     "quote": project__.quote, "workOrder": project__.work_order, "customer": customer__
                        #                 }
                        rows___.append(case_list)

                    cases__.append(rows___)
                    units__.append(unit_list)
                    others__.append(other_val_list)
                    try:
                        act_dict_ = {'v_type': cases[0].ratedCv, 'trim_type': v_details.trimType__.name, 'Balancing': v_details.balanceSeal__.name,
                                    'fl_direction': v_details.flowDirection__.name, 'v_size': cases[0].valveSize,
                                    'v_size_unit': item.project.lengthUnit,
                                    'Seat_Dia': i.seatDia,
                                    'seat_dia_unit': item.project.lengthUnit, 'unbalance_area': act_valve_data_string[5],
                                    'unbalance_area_unit': 'inch^2',
                                    'Stem_size': act_valve_data_string[4], 'Stem_size_unit': 'inch',
                                    'Travel': act_valve_data_string[1],
                                    'travel_unit': 'inch', 'Packing_Friction': act_data_string[13],
                                    'packing_friction_unit': 'mm', 'Seat_Load_Factor': act_data_string[24],
                                    'Additional_Factor': 0,
                                    'P1': itemCases_1[-1].iPressure,
                                    'p1_unit': item.project.pressureUnit,
                                    'P2': itemCases_1[-1].oPressure, 'p2_unit': item.project.pressureUnit,
                                    'delP_Shutoff': v_details.shutOffDelP, 'delP_Shutoff_unit': 'bar', 'unbal_force': 0,
                                    'Kn': act_data_string[15], 'delP_flowing': 0,
                                    'act_type': act_other[0],
                                    'fail_action': act_data_string[4], 'act_size': act_data_string[0],
                                    'act_size_unit': 'inch',
                                    'act_travel': act_data_string[1], 'act_travel_unit': 'inch',
                                    'eff_area': act_data_string[0], 'eff_area_unit': 'inch^2',
                                    'sMin': act_data_string[2], 'sMax': act_data_string[3], 'spring_rate': act_data_string[18],
                                    'spring_windup': act_data_string[19], 'max_spring_load': act_data_string[20],
                                    'max_air_supply': act_other[6],
                                    'set_pressure': act_data_string[5], 'set_pressure_unit': 'bar', 'act_thrust_down': 0,
                                    'act_thrust_up': 0, 'handwheel': act_other[2],
                                    'friction_band': act_data_string[21],
                                    'req_handWheel_thrust': act_data_string[22], 'max_thrust': act_data_string[23],
                                    'v_thrust_close': 0, 'v_thrust_open': 0, 'seat_load': act_data_string[14],
                                    'orientation': act_other[3], 'act_model': act_model, 'travel_stops': act_other[8]
                                    }
                    except IndexError:
                        act_dict_ = {'v_type': cases[0].ratedCv, 'trim_type': v_details.trimType__.name, 'Balancing': v_details.balanceSeal__.name,
                                    'fl_direction':  v_details.flowDirection__.name, 'v_size': cases[0].valveSize,
                                    'v_size_unit': item.project.lengthUnit,
                                    'Seat_Dia': i.seatDia,
                                    'seat_dia_unit': item.project.lengthUnit, 'unbalance_area': None,
                                    'unbalance_area_unit': 'inch^2',
                                    'Stem_size': None, 'Stem_size_unit': 'inch',
                                    'Travel': None,
                                    'travel_unit': 'inch', 'Packing_Friction': None,
                                    'packing_friction_unit': 'mm', 'Seat_Load_Factor': None,
                                    'Additional_Factor': 0,
                                    'P1': itemCases_1[-1].inletPressure,
                                    'p1_unit': item.project.pressureUnit,
                                    'P2': itemCases_1[-1].outletPressure, 'p2_unit': item.project.pressureUnit,
                                    'delP_Shutoff': v_details.shutOffDelP, 'delP_Shutoff_unit': 'bar', 'unbal_force': 0,
                                    'Kn': None, 'delP_flowing': 0,
                                    'act_type': None,
                                    'fail_action': None, 'act_size': None,
                                    'act_size_unit': 'inch',
                                    'act_travel': None, 'act_travel_unit': 'inch',
                                    'eff_area': None, 'eff_area_unit': 'inch^2',
                                    'sMin': None, 'sMax': None, 'spring_rate': None,
                                    'spring_windup': None, 'max_spring_load': None,
                                    'max_air_supply': None,
                                    'set_pressure': None, 'set_pressure_unit': 'bar', 'act_thrust_down': 0,
                                    'act_thrust_up': 0, 'handwheel': None,
                                    'friction_band': None,
                                    'req_handWheel_thrust': None, 'max_thrust': None,
                                    'v_thrust_close': 0, 'v_thrust_open': 0, 'seat_load': None,
                                    'orientation': None, 'act_model': act_model, 'travel_stops': None
                                    }
                    act_dict = act_dict_

            print(act_dict)
            createSpecSheet(cases__, units__, others__, act_dict)
            path = "specsheet.xlsx"
            project_number = item.project.id
            current_datetime = datetime.datetime.today().date().timetuple()

            str_current_datetime = str(current_datetime)
            a__ = datetime.datetime.now()
            a_ = a__.strftime("%a, %d %b %Y %H-%M-%S")
            spec_sheet_name = f'ControlValveSpecification{project_number}_{a_}.xlsx'

            return send_file(path, as_attachment=True, download_name=spec_sheet_name)
    except Exception as e:
        # flash(f'some error occured: {e}')
        flash('Data missing')
        print(f'Generate CSV Issue: {e}')
        return redirect(url_for(page, item_id=item_id, proj_id=proj_id))


@app.route('/export-project/proj-<proj_id>/item-<item_id>', methods=['GET', 'POST'])
def exportProject(item_id, proj_id):
    try:
        project_element = getDBElementWithId(projectMaster, proj_id)
        project_elements = db.session.query(projectMaster).filter_by(id=proj_id).all()
        all_items = db.session.query(itemMaster).filter_by(project=project_element).all()
        with open('my_file.csv', 'w', newline='') as csvfile:
            # Create a CSV writer object
            writer = csv.writer(csvfile)
            # Add Project Elements
            # Write data to the CSV file
            all_keys = projectMaster.__table__.columns.keys()
            all_keys.remove('createdById')
            writer.writerow(all_keys)
            for data_ in project_elements:
                single_row_data = []
                for key_ in all_keys:
                    if key_ != 'createdById':
                        # print(key_, projectMaster.__table__.columns[key_].type)
                    # all_data[0][all_keys[1]]
                        abc = getattr(data_, key_)
                        if key_ == 'IndustryId':
                            abc_name = getDBElementWithId(industryMaster, int(abc))
                            single_row_data.append(abc_name.name)
                        elif key_ == 'regionID':
                            abc_name = getDBElementWithId(regionMaster, int(abc))
                            single_row_data.append(abc_name.name)
                        elif key_ == 'revisionNo':
                            single_row_data.append(1)
                        else:
                            single_row_data.append(abc)
                writer.writerow(single_row_data)
            
            # Add items Elements
            all_keys_item = itemMaster.__table__.columns.keys()
            all_keys_item_valve = valveDetailsMaster.__table__.columns.keys()
            allkeys_item = all_keys_item + all_keys_item_valve
            print('valve item keys')
            print(allkeys_item)
            writer.writerow(allkeys_item)
            for data_ in all_items:
                single_row_data = []
                for key_ in all_keys_item:
                    abc = getattr(data_, key_)
                    single_row_data.append(abc)

                valve_item = db.session.query(valveDetailsMaster).filter_by(item=data_).first()
                single_row_data_valve = []
                for key_ in all_keys_item_valve[:15]:
                    abc = getattr(valve_item, key_)
                    single_row_data_valve.append(abc)
                # writer.writerow(single_row_data_valve)
                single_row_data_valve_name = []
                for key_ in all_keys_item_valve[15:]:
                    if key_ not in ['nde1', 'nde2']:
                        table_element = valve_table_dict_two[key_]
                        abc = getattr(valve_item, key_) # get id of the table
                        try:
                            query_set = getDBElementWithId(table_element, int(abc))
                            single_row_data_valve_name.append(query_set.name)
                            print(table_element.__tablename__, abc, query_set.name)
                        except:
                            single_row_data_valve_name.append('')
                        
                    else:
                        single_row_data_valve_name.append('')
                valve_data_all_list = single_row_data + single_row_data_valve + single_row_data_valve_name
                writer.writerow(valve_data_all_list)
            
            # Add Case Elements

            all_keys_cases = caseMaster.__table__.columns.keys()
            writer.writerow(all_keys_cases)
            for item_ in all_items:
                cases_ = db.session.query(caseMaster).filter_by(item=item_).all()
                all_row_data_case = []
                for case_ in cases_:
                    single_row_data_case = []
                    for key_ in all_keys_cases:
                        if key_ not in ['valveDiaId', 'fluidId']:
                            abc = getattr(case_, key_)
                            single_row_data_case.append(abc)
                        elif key_ == 'valveDiaId':
                            try:
                                valve_element = getDBElementWithId(cvTable, int(key_))
                                single_row_data_case.append(valve_element.valveSize)
                            except:
                                single_row_data_case.append("")
                        elif key_ == 'fluidId':
                            try:
                                fluid_element = getDBElementWithId(fluidProperties, int(key_))
                                single_row_data_case.append(fluid_element.fluidName)
                            except:
                                single_row_data_case.append("")               
                    writer.writerow(single_row_data_case)
            csvfile.close()
        path = 'my_file.csv'
        return send_file(path, as_attachment=True, download_name=f"{projectMaster.__tablename__}.csv")
    except Exception as e:
        return f'Something happened: {e}'
    # return f"{len(all_items)}"
    # pass


@app.route('/import-project/proj-<proj_id>/item-<item_id>', methods=['GET', 'POST'])
def importProject(item_id, proj_id):
    len_project = len(projectMaster.query.all())
    quote_no = f"Q{date_today[2:4]}0000{len_project}"
    if request.method == 'POST':
        # try:
        all_keys = projectMaster.__table__.columns.keys()
        # Parse data from CSV Uploaded file, filestorage component
        b_list = request.files.get('file').stream.read().decode('latin-1').strip().split('\n')
        part_list = []
        b_split_list = []
        for data_ in b_list:
            data_split = data_.split(',')
            b_split_list.append(data_split)

        for i in b_split_list:
            if i[0] == 'id':
                index_id = b_split_list.index(i)
                part_list.append(index_id)
        proj_list = b_split_list[1]
        item_list = b_split_list[(part_list[1]+1):(part_list[2])]
        print(item_list)
        cases_list = b_split_list[(part_list[2] + 1):]

        # Check correct file or not:
        if all_keys[:7] == b_split_list[0][:7]:
            print("Headers Match")
        else:
            print("Headers Mismatch")

        # add project
        industry_element = industryMaster.query.filter(industryMaster.name.like(proj_list[16]))
        try:
            region_element = regionMaster.query.filter(regionMaster.name.ilike(str(proj_list[17])))
            print(region_element[0].name)
            region_ = region_element[0]
        except IndexError:
            region_element = regionMaster.query.filter(regionMaster.name.ilike(str(proj_list[17][:-2])))
            region_ = None

        new_project = projectMaster(
            projectId=quote_no,
            projectRef=proj_list[2],
            enquiryRef=proj_list[3],
            enquiryReceivedDate=datetime.datetime.strptime(parse(str(proj_list[4][:10])).strftime("%Y-%m-%d"), "%Y-%m-%d"),
            receiptDate=datetime.datetime.strptime(parse(str(proj_list[5][:10])).strftime("%Y-%m-%d"), "%Y-%m-%d"),
            bidDueDate=datetime.datetime.strptime(parse(str(proj_list[6][:10])).strftime("%Y-%m-%d"), "%Y-%m-%d"),
            purpose=proj_list[7],
            custPoNo=proj_list[8],
            workOderNo=proj_list[9],
            revisionNo=proj_list[10],
            status=proj_list[11],
            pressureUnit=proj_list[12],
            flowrateUnit=proj_list[14],
            temperatureUnit=proj_list[14],
            lengthUnit=proj_list[15],
            industry=industry_element[0],
            region=region_,
            user=current_user
            )
        db.session.add(new_project)
        db.session.commit()

        # add items
        all_keys_cases = caseMaster.__table__.columns.keys()
        for item_ in item_list:
            print('Adding item')
            new_item = itemMaster(
                itemNumber=item_[1],
                alternate=item_[2],
                standardStatus=getBooleanFromString(item_[3]),
                pipeDataStatus=getBooleanFromString(item_[4]),
                flowrate_unit=item_[5],
                inpres_unit=item_[6],
                outpres_unit=item_[7],
                intemp_unit=item_[8],
                vaporpres_unit=item_[9],
                criticalpres_unit=item_[10],
                inpipe_unit=item_[11],
                outpipe_unit=item_[12],
                valvesize_unit=item_[13],
                project=new_project
                )
            db.session.add(new_item)
            db.session.commit()
            new_valve = valveDetailsMaster(
                item=new_item,
                quantity=float_convert(item_[5+11]),
                tagNumber=item_[6+11],
                serialNumber=item_[7+11],
                shutOffDelP=float_convert(item_[8+11]),
                maxPressure=float_convert(item_[9+11]),
                maxTemp=float_convert(item_[10+11]),
                minTemp=float_convert(item_[11+11]),
                shutOffDelPUnit=item_[12+11],
                maxPressureUnit=item_[13+11],
                maxTempUnit=item_[14+11],
                minTempUnit=item_[15+11],
                bonnetExtDimension=float_convert(item_[16+11]),
                application=item_[17+11],
                rating=getDBElementWithName(ratingMaster, item_[19+11]),
                material=getDBElementWithName(materialMaster, item_[20+11]),
                design=getDBElementWithName(designStandard, item_[21+11]),
                style=getDBElementWithName(valveStyle, item_[22+11]),
                state=getDBElementWithName(fluidState, item_[23+11]),
                endConnection__=getDBElementWithName(endConnection, item_[24+11]),
                endFinish__=getDBElementWithName(endFinish, item_[25+11]),
                bonnetType__=getDBElementWithName(bonnetType, item_[26+11]),
                packingType__=getDBElementWithName(packingType, item_[27+11]),
                trimType__=getDBElementWithName(trimType, item_[28+11]),
                flowCharacter__=getDBElementWithName(flowCharacter, item_[29+11]),
                flowDirection__=getDBElementWithName(flowDirection, item_[30+11]),
                seatLeakageClass__=getDBElementWithName(seatLeakageClass, item_[31+11]),
                bonnet__=getDBElementWithName(bonnet, item_[32+11]),
                nde1__=None,
                nde2__=None,
                shaft__=getDBElementWithName(shaft, item_[35+11]),
                disc__=getDBElementWithName(disc, item_[36+11]),
                seat__=getDBElementWithName(seat, item_[37+11]),
                packing__=getDBElementWithName(packing, item_[38+11]),
                balanceSeal__=getDBElementWithName(balanceSeal, item_[39+11]),
                studNut__=getDBElementWithName(studNut, item_[40+11]),
                gasket__=getDBElementWithName(gasket, item_[41+11]),
                cage__=getDBElementWithName(cageClamp, item_[42+11]),
                )
            db.session.add(new_valve)

            new_actuator = actuatorMaster(item=new_item)
            db.session.add(new_actuator)
            db.session.commit()
            new_accessories = accessoriesData(item=new_item)
            db.session.add(new_accessories)
            db.session.commit()
            
            # add cases
            for case_ in cases_list:
                if int(case_[-2] ) == int(item_[0]):
                    new_case = caseMaster(item=new_item)
                    db.session.add(new_case)
                    db.session.commit()

                    all_cases = db.session.query(caseMaster).filter_by(item=new_item).all()
                    case_update_dict = {}
                    for index_ in range(len(all_keys_cases)):
                        case_update_dict[all_keys_cases[index_]] = float_convert(case_[index_])

                    case_id = case_update_dict.pop('id')
                    iSch = case_update_dict.pop('inletPipeSchId')
                    valveDiaId = case_update_dict.pop('valveDiaId')
                    itemId = case_update_dict.pop('itemId')
                    fluidId = case_update_dict.pop('fluidId')
                    # case_update_dict['item'] = new_item
                    case_update_dict['cv'] = getDBElementWithId(cvTable, valveDiaId)
                    case_update_dict['fluid'] = getDBElementWithName(fluidProperties, fluidId)
                    
                    new_case.update(case_update_dict, all_cases[-1].id)
            
        
        flash('Project Imported Successfully')
        # except Exception as e:
        #     flash('Something Went Wrong')
        #     print(f'This is what went wrong: {e}')
        return redirect(url_for('home', item_id=item_id, proj_id=proj_id))

    return render_template('projectImport.html', item=getDBElementWithId(itemMaster, int(item_id)), page='importProject', user=current_user)


@app.route('/export-item/proj-<proj_id>/item-<item_id>', methods=['GET', 'POST'])
def exportItem(item_id, proj_id):
    all_items = db.session.query(itemMaster).filter_by(id=int(item_id)).all()
    with open('my_file.csv', 'w', newline='') as csvfile:
        # Create a CSV writer object
        writer = csv.writer(csvfile)
        # Add items Elements
        all_keys_item = itemMaster.__table__.columns.keys()
        all_keys_item_valve = valveDetailsMaster.__table__.columns.keys()
        allkeys_item = all_keys_item + all_keys_item_valve
        print('valve item keys')
        print(allkeys_item)
        writer.writerow(allkeys_item)
        for data_ in all_items:
            single_row_data = []
            for key_ in all_keys_item:
                abc = getattr(data_, key_)
                single_row_data.append(abc)

            valve_item = db.session.query(valveDetailsMaster).filter_by(item=data_).first()
            single_row_data_valve = []
            for key_ in all_keys_item_valve[:15]:
                abc = getattr(valve_item, key_)
                single_row_data_valve.append(abc)
            # writer.writerow(single_row_data_valve)
            single_row_data_valve_name = []
            for key_ in all_keys_item_valve[15:]:
                if key_ not in ['nde1', 'nde2']:
                    table_element = valve_table_dict_two[key_]
                    abc = getattr(valve_item, key_) # get id of the table
                    try:
                        query_set = getDBElementWithId(table_element, int(abc))
                        single_row_data_valve_name.append(query_set.name)
                        print(table_element.__tablename__, abc, query_set.name)
                    except:
                        single_row_data_valve_name.append('')
                    
                else:
                    single_row_data_valve_name.append('')
            valve_data_all_list = single_row_data + single_row_data_valve + single_row_data_valve_name
            writer.writerow(valve_data_all_list)
        
        # Add Case Elements

        all_keys_cases = caseMaster.__table__.columns.keys()
        writer.writerow(all_keys_cases)
        for item_ in all_items:
            cases_ = db.session.query(caseMaster).filter_by(item=item_).all()
            for case_ in cases_:
                single_row_data_case = []
                for key_ in all_keys_cases:
                    if key_ not in ['valveDiaId', 'fluidId']:
                        abc = getattr(case_, key_)
                        single_row_data_case.append(abc)
                    elif key_ == 'valveDiaId':
                        try:
                            valve_element = getDBElementWithId(cvTable, int(key_))
                            single_row_data_case.append(valve_element.valveSize)
                        except:
                            single_row_data_case.append("")
                    elif key_ == 'fluidId':
                        try:
                            fluid_element = getDBElementWithId(fluidProperties, int(key_))
                            single_row_data_case.append(fluid_element.fluidName)
                        except:
                            single_row_data_case.append("")               
                writer.writerow(single_row_data_case)
        csvfile.close()
    path = 'my_file.csv'
    return send_file(path, as_attachment=True, download_name=f"{itemMaster.__tablename__}.csv")
    # return f"{len(all_items)}"


@app.route('/import-item/proj-<proj_id>/item-<item_id>', methods=['GET', 'POST'])
def importItem(item_id, proj_id):
    item_element = getDBElementWithId(itemMaster, int(item_id))
    project_element = getDBElementWithId(projectMaster, int(item_element.projectID))
    if request.method == 'POST':
        try:
            # Parse data from CSV Uploaded file, filestorage component
            b_list = request.files.get('file').stream.read().decode('latin-1').strip().split('\n')
            part_list = []
            b_split_list = []
            for data_ in b_list:
                data_split = data_.split(',')
                b_split_list.append(data_split)

            for i in b_split_list:
                if i[0] == 'id':
                    index_id = b_split_list.index(i)
                    part_list.append(index_id)
            item_list = b_split_list[1]
            cases_list = b_split_list[(part_list[1]+1):]
            # add items
            all_keys_cases = caseMaster.__table__.columns.keys()
            for item_ in item_list:
                print('Adding item')
                new_item = itemMaster(
                    itemNumber=item_[1],
                    alternate=item_[2],
                    project=project_element
                    )
                db.session.add(new_item)
                db.session.commit()
                new_valve = valveDetailsMaster(
                    item=new_item,
                    quantity=item_[5],
                    tagNumber=item_[6],
                    serialNumber=item_[7],
                    shutOffDelP=float(item_[8]),
                    maxPressure=float(item_[9]),
                    maxTemp=float(item_[10]),
                    minTemp=float(item_[11]),
                    shutOffDelPUnit=item_[12],
                    maxPressureUnit=item_[13],
                    maxTempUnit=item_[14],
                    minTempUnit=item_[15],
                    bonnetExtDimension=item_[16],
                    application=item_[17],
                    rating=getDBElementWithName(ratingMaster, item_[19]),
                    material=getDBElementWithName(materialMaster, item_[20]),
                    design=getDBElementWithName(designStandard, item_[21]),
                    style=getDBElementWithName(valveStyle, item_[22]),
                    state=getDBElementWithName(fluidState, item_[23]),
                    endConnection__=getDBElementWithName(endConnection, item_[24]),
                    endFinish__=getDBElementWithName(endFinish, item_[25]),
                    bonnetType__=getDBElementWithName(bonnetType, item_[26]),
                    packingType__=getDBElementWithName(packingType, item_[27]),
                    trimType__=getDBElementWithName(trimType, item_[28]),
                    flowCharacter__=getDBElementWithName(flowCharacter, item_[29]),
                    flowDirection__=getDBElementWithName(flowDirection, item_[30]),
                    seatLeakageClass__=getDBElementWithName(seatLeakageClass, item_[31]),
                    bonnet__=getDBElementWithName(bonnet, item_[32]),
                    nde1__=None,
                    nde2__=None,
                    shaft__=getDBElementWithName(shaft, item_[35]),
                    disc__=getDBElementWithName(disc, item_[36]),
                    seat__=getDBElementWithName(seat, item_[37]),
                    packing__=getDBElementWithName(packing, item_[38]),
                    balanceSeal__=getDBElementWithName(balanceSeal, item_[39]),
                    studNut__=getDBElementWithName(studNut, item_[40]),
                    gasket__=getDBElementWithName(gasket, item_[41]),
                    cage__=getDBElementWithName(cageClamp, item_[42]),
                    )
                db.session.add(new_valve)

                new_actuator = actuatorMaster(item=new_item)
                db.session.add(new_actuator)
                db.session.commit()
                new_accessories = accessoriesData(item=new_item)
                db.session.add(new_accessories)
                db.session.commit()
                
                # add cases
                for case_ in cases_list:
                    if int(case_[-2] ) == int(item_[0]):
                        new_case = caseMaster(item=new_item)
                        db.session.add(new_case)
                        db.session.commit()

                        all_cases = db.session.query(caseMaster).filter_by(item=new_item).all()
                        case_update_dict = {}
                        for index_ in range(len(all_keys_cases)):
                            case_update_dict[all_keys_cases[index_]] = float_convert(case_[index_])

                        case_id = case_update_dict.pop('id')
                        iSch = case_update_dict.pop('inletPipeSchId')
                        valveDiaId = case_update_dict.pop('valveDiaId')
                        itemId = case_update_dict.pop('itemId')
                        fluidId = case_update_dict.pop('fluidId')
                        # case_update_dict['item'] = new_item
                        case_update_dict['cv'] = getDBElementWithId(cvTable, valveDiaId)
                        case_update_dict['fluid'] = getDBElementWithName(fluidProperties, fluidId)
                        
                        new_case.update(case_update_dict, all_cases[-1].id)
               
            
            flash('Project Imported Successfully')
        except:
            flash('Something Went Wrong')
        return redirect(url_for('home', item_id=item_id, proj_id=proj_id))

    return render_template('projectImport.html', item=getDBElementWithId(itemMaster, int(item_id)), page='importProject', user=current_user)


# Admin Panel
@app.route('/admin-panel/proj-<proj_id>/item-<item_id>', methods=['GET', 'POST'])
def adminPanel(item_id, proj_id):
    users = userMaster.query.all()
    first_user = users[0].id
    return render_template('admin.html', item=getDBElementWithId(itemMaster, int(item_id)), 
                           page='adminPanel', user=current_user, user_id=first_user)


@app.route('/isUserExist', methods=['GET', 'POST'])
def isUserExist():
    emailID = request.args.get('emailID')
    if userMaster.query.filter_by(email=emailID).first():
        # user already exists
        json_ = {'message': 'Email ID already exists'}
        return jsonify(json_)
    else:
        json_ = {'message': 'New User'}
        return jsonify(json_)


@app.route('/admin-new-user/proj-<proj_id>/item-<item_id>', methods=['GET', 'POST'])
def adminNewUser(item_id, proj_id):
    designations_ = designationMaster.query.all()
    departments_ = departmentMaster.query.all()
    if request.method == 'POST':
        if userMaster.query.filter_by(email=request.form['email']).first():
            # user already exists
            flash("Email-ID already exists")
            return redirect(url_for('adminNewUser', item_id=item_id, proj_id=proj_id))
        else:
            department_element = departmentMaster.query.get(int(request.form['department']))
            designation_element = designationMaster.query.get(int(request.form['designation']))
            new_user = userMaster(email=request.form['email'],
                                  password=generate_password_hash(request.form['password'], method='pbkdf2:sha256',
                                                                  salt_length=8),
                                  name=request.form['name'],
                                  employeeId=request.form['employeeId'],
                                  mobile=request.form['mobile'],
                                  designation=designation_element,
                                  department=department_element,
                                  fccUser=True
                                  )
            db.session.add(new_user)
            db.session.commit()

            if department_element.name == "Application Engineering, Sales & Contracts":
                addUserAsEng(request.form['name'], designation_element.name)

            # Add Project and Item
            flash('New User Added Successfully')
            newUserProjectItem(user=new_user)
    return render_template('admin-new-user.html', item=getDBElementWithId(itemMaster, int(item_id)), 
                           page='adminNewUser', user=current_user, designations=designations_,
                           departments=departments_)


@app.route('/admin-edit-user/proj-<proj_id>/item-<item_id>/user-<user_id>', methods=['GET', 'POST'])
def adminEditUser(item_id, proj_id, user_id):
    user_element = getDBElementWithId(userMaster, int(user_id))
    designations_ = designationMaster.query.all()
    departments_ = departmentMaster.query.all()
    allUsers = userMaster.query.all()
    return render_template('admin-edit-user.html', item=getDBElementWithId(itemMaster, int(item_id)), 
                           page='adminEditUser', user=current_user, designations=designations_,
                           departments=departments_, users=allUsers, user_select=user_element)


@app.route('/admin-user-rights/proj-<proj_id>/item-<item_id>', methods=['GET', 'POST'])
def adminUserRights(item_id, proj_id):
    return render_template('user-rights.html', item=getDBElementWithId(itemMaster, int(item_id)), page='adminUserRights', user=current_user)



####################### DATA UPLOAD BULK
def DATA_UPLOAD_BULK():    
    industry_list = ['Oil & Gas - Onshore', 'Oil & Gas - Offshore', 'Refinery & Petrochemical',
                    'Oil & Gas - Transportation & Distribution', 'Chem & Pharma', 'Food & Beverages', 'OEM',
                    'Pulp & Paper', 'Mining & Metal', 'Thermal Power & Nuclear Power', 'Defence, Nuclear & Aerospace',
                    'Air Separation & LNG', 'Desalination & Water Treatment Plant', 'Others']

    region_list = ['Domestic', 'South East Asia', 'China', 'Australia', 'Europe', 'Middle East', 'Africa', 'Far East',
                'Russia', 'North America', 'South America', 'Special Project']

    f_state_list = ['Liquid', 'Gas', 'Two Phase']

    design_std_list = ['ASME', 'API']

    valve_style_list = ['Globe Straight', 'Globe Angle', 'Butterfly Lugged Wafer', 'Butterfly Double Flanged']

    application_list = ['Temperature Control', 'Pressure Control', 'Flow Control', 'Level Control', 'Compressor Re-Cycle',
                        'Compressor Anti-Surge', 'Cold Box Service', 'Condensate Service', 'Cryogenic Service',
                        'Desuperheater Service', 'Feedwater Service', 'Heater Drain', 'High P&T Steam', 'H/He Service',
                        'Joule Thompson Valve', 'LNG Service', 'Soot Blower Valve', 'Spraywater Valve', 'Switching Valve']

    rating_list = ['ASME 150', 'ASME 300', 'ASME 600', 'ASME 900', 'ASME 1500', 'ASME 2500', 'API 5000', 'API 10000',
                'API 15000']

    material_list = ['ASTM A216 WCB', 'ASTM A216 WCC', 'ASTM A352 LCC', 'ASTM A352 LCB', 'ASTM A351 CF8M',
                    'ASTM A351 CF3M', 'ASTM A351 CF8', 'ASTM A351 CF3', 'ASTM A217 WC6', 'ASTM A217 WC9',
                    'ASTM A217 C12A', 'ASTM A217 C5', 'ASTM A995 CD3MN (4A)', 'ASTM A995 CE8MN (5A)',
                    'ASTM A995 CD3MWCuN (6A)', 'ASTM A351 CK3MCuN']

    balance_seal_list = ['Unbalanced', 'Balanced PTFE', 'Balanced Graphite', 'Metal']

    bonnet_list = ['ASTM A216 WCB', 'ASTM A216 WCC', 'ASTM A352 LCC', 'ASTM A352 LCB', 'ASTM A351 CF8M',
                    'ASTM A351 CF3M', 'ASTM A351 CF8', 'ASTM A351 CF3', 'ASTM A217 WC6', 'ASTM A217 WC9',
                    'ASTM A217 C12A', 'ASTM A217 C5', 'ASTM A995 CD3MN (4A)', 'ASTM A995 CE8MN (5A)',
                    'ASTM A995 CD3MWCuN (6A)', 'ASTM A351 CK3MCuN']

    bonnetType_list = ['Standard', 'Standard Extension', 'Normalised/Finned', "Bellow Seal", 'Cryogenic',
                        'Cryogenic + Drip Plate', 'Cryogenic + Seal Boot', 'Cryogenic + Cold Box Flange']

    certification_list = ['2.1 Certification', '2.2 Certification', '3.1 Certification', '3.2 Certification', 'NABL Certified']

    cleaning_list = ['As per FCC Standard', 'As per Customer specification']

    flow_dir_list = ['Over', 'Under', 'Seat Downstream', 'Seat Upstream']

    trim_type_list_globe = ['Microspline', 'Contour', 'Ported', 'Anti-Cavitation I', 'Anti-Cavitation II', 'Anti-Cavitation III', 'MHC',
                    'Low Noise Trim A1','Low Noise Trim A3','Low Noise Trim B1','Low Noise Trim B3','Low Noise Trim C1',
                    'Low Noise Trim C3','Low Noise Trim D1','Low Noise Trim D3']

    trim_type_list_butterfly = ['Double Offset', 'Triple Offset']


    flow_charac_list = ['Equal %', 'Linear', 'Modified Equal %']

    balancing_list = ['Balanced', 'Unbalanced', 'N/A']

    disc_material_list_butterfly = ['316SS', '316 / Stellite Overlay', '316L SS', '316L / Stellite Overlay', 'UNS 31254 / 6Mo',
                                    'UNS 31803 / DSS', 'Al. Bronze', 'UNS 32760 / SDSS', 'Hastelloy C', 'Alloy 625', 'Monel 400', 
                                    'Monel 500', 'Titanium', 'Alloy 800']

    plug_material_list_globe = ['316SS', '304SS', '304SS / Stellite FC', '304SS / Stellite SA', '304L SS', '304L SS / Stellite FC', '304L SS / Stellite SA',
                                '316 SS / Stellite FC', '316 SS / Stellite SA', '316L SS', '316L SS / Stellite FC', '316L SS / Stellite SA',
                                '410SS', '410SS Hardened', '440C SS Hardened', 'Al. Bronze', 'Duplex SS', 'Duplex SS / Stellite FC', 'Duplex SS / Stellite SA',
                                'Hastelloy B', 'Hastelloy C', 'Alloy 625', 'Alloy 625 / Stellite FC', 'Alloy 625 / Stellite SA', 'Monel 400 / K500',
                                'Monel / Col / LG2', 'Super Duplex SS', 'Super Duplex SS / Stellite FC', 'Super Duplex SS / Stellite SA', 'Tungsten. Co / 17-4PH',
                                'Tungsten. Co / 316SS']

    seat_material_list_globe = ['S41000', 'S31600 w/CoCr-A SA', 'S316 w/CoCr-A FC', 'CA6NM HT', '2205 Duplex w/CoCr-A', 
                                '2507 Super Duplex w/CoCr-A', 'PTFE']

    seat_material_list_butterfly = ['PTFE', '316SS', 'S32760', 'Alloy 625', 'Laminated 316L + Graphite', 'Laminated 625 + Graphite']

    packing_material_list_butterfly = ['PTFE Chevron', 'PTFE Braid', 'Graphite', 'RPTFE Graphite', 'Low Emmission EVSP', 'High Intensity Gland', 
                                    'HIG Spagrapf', 'Gland Security System', 'Packing + Wiper PTFE', 'Packing + Wiper Graphite']

    designation_list = ['Manager','Director','Managing Director','Sr.Manager','Assistant Manager','Deputy Manager','Engineer',
                        'GET','Ass.Engineer','Sr. Engineer','Executive','Technician']

    department_list = ['Finance & HR', 'Administration', 'Finance', 'Design & Engineering', 'Application Engineering, Sales & Contracts',
                    'Purchase', 'Quality Control', 'Information Technology', 'Production', 'Production & Maintenance']

    end_connection_list = ['None', 'Integral Flange', 'Loose Flange', 'Flange (Drilled ASME 150)', 'Screwed NPT', 'Screwed BSPT', 
                        'Screwed BSP', 'Socket Weld', 'Butt Weld', 'Grayloc Hub', 'Vector / Techloc Hub', 'Destec Hub', 
                        'Galperti Hub', 'BW Stubs', 'Plain Stubs', 'Drilled Lug', 'Tapped Lug', 'BW Stubs Sch 10', 'BW Stubs Sch 40', 
                        'BW Stubs Sch 80']

    end_finish_list = ['None', 'RF Serrated', 'RF (125-250 AARH) 3.2-6.3 μm', 'RF (63-125 AARH) 1.6-3.2 μm', 'FF Serrated',
                    'FF (125-250 AARH) 3.2-6.3 μm', 'FF (63-125 AARH) 1.6-3.2 μm', 'RTJ', 'ASME B16.21 Fig. 2a']

    seat_leakage_class_list = ['ANSI Class II', 'ANSI Class III', 'ANSI Class IV', 'ANSI Class V', 'ANSI Class VI']

    stud_material_list = ['None', 'Standard for Body Material', 'B7 / 2H', 'B7 / 2H Galvanised', 'L7 / 4', 'L7 / 7 Xylan Coated', 
                        'L7M / 7M', 'B8M / 8M', 'B8 Class 1/8', 'B8 / 8', 'Al-Br B150 Gr C6300 HR50', 'B7M / 2HM', 'B16 / 4']

    gasket_material_list = ['Standard for Service', 'PTFE', 'PCTFE (KEL-F)', 'Spiral Wond 316L / Graph.', 
                            'Spiral Wond 316L / PTFE', 'Spiral Wond 31803 / Graph.', 'Spiral Wond 31803 / PTFE', 
                            'Spiral Wond 32760 / Graph.', 'Spiral Wond 32760 / PTFE', 'Spiral Wond 625 / Graph.', 
                            'Spiral Wond 625 / PTFE', 'Graphite', 'Metal Seal', 'Double ABS (cryo)']

    cage_clamp_material_list = ["316", "17-4PH", "17-4PH (H900)", "316 Cr Plated", 
                                "32760 (Super Duplex)",  "31803 Duplex", "410"]


    packing_type_list = ['Single', 'Double', 'Inverted']



    # print(getRowsFromCsvFile("csv/afr.csv"))
    # print(getRowsFromCsvFile("csv/cvtable.csv")[::6])
    # print(getRowsFromCsvFile("csv/shaft.csv"))


    with app.app_context():
        # data_upload(valve_style_list, valveStyle)
        butterfly_element_1 = db.session.query(valveStyle).filter_by(name="Butterfly Lugged Wafer").first()
        butterfly_element_2 = db.session.query(valveStyle).filter_by(name="Butterfly Double Flanged").first()
        globe_element_1 = db.session.query(valveStyle).filter_by(name="Globe Straight").first()
        globe_element_2 = db.session.query(valveStyle).filter_by(name="Globe Angle").first()
        v_style_list = [butterfly_element_1, butterfly_element_2, globe_element_1, globe_element_2]   
        # data_upload(industry_list, industryMaster)
        # data_upload(region_list, regionMaster)
        # data_upload(f_state_list, fluidState)
        # data_upload(design_std_list, designStandard)
        # data_upload(application_list, applicationMaster)
        # data_upload(rating_list, ratingMaster)
        # data_upload(material_list, materialMaster)
        # data_upload(bonnet_list, bonnet)
        # add_many(getRowsFromCsvFile("csv/afr.csv"), afr)
        # add_many(getRowsFromCsvFile("csv/fluidProperties.csv"), fluidProperties)
        # add_many(getRowsFromCsvFile("csv/pipearea.csv"), pipeArea)
        # add_many(getRowsFromCsvFile("csv/valvearea.csv"), valveArea)
        # data_upload(balance_seal_list, balanceSeal)
        # data_upload(bonnetType_list, bonnetType)
        # data_upload(certification_list, certification)
        # data_upload(cleaning_list, cleaning)
        # data_upload(flow_dir_list, flowDirection)
        # # data_upload(trim_type_list, trimType)
        # data_upload(flow_charac_list, flowCharacter)
        # data_upload(balancing_list, balancing)
        # # cv_upload(getRowsFromCsvFile("csv/cvtable_small.csv"))
        # # cv_upload(getRowsFromCsvFile("csv/cvtable.csv"))
        # data_upload_disc_seat_packing([disc_material_list_butterfly, disc_material_list_butterfly, plug_material_list_globe, plug_material_list_globe], v_style_list, disc)
        # data_upload_disc_seat_packing([seat_material_list_butterfly, seat_material_list_butterfly, seat_material_list_globe, seat_material_list_globe], v_style_list, seat)
        # data_upload_disc_seat_packing([trim_type_list_butterfly, trim_type_list_butterfly, trim_type_list_globe, trim_type_list_globe], v_style_list, trimType)
        # data_upload(department_list, departmentMaster)
        # data_upload(designation_list, designationMaster)
        # data_upload_shaft(getRowsFromCsvFile("csv/shaft.csv"), v_style_list)
        # data_upload(end_connection_list, endConnection)
        # data_upload(end_finish_list, endFinish)
        # data_upload(seat_leakage_class_list, seatLeakageClass)
        # data_upload(packing_material_list_butterfly, packing)
        # data_upload(stud_material_list, studNut)
        # data_upload(gasket_material_list, gasket)
        # data_upload(cage_clamp_material_list, cageClamp)
        # data_upload(packing_type_list, packingType)
        # add_many(getRowsFromCsvFile("csv/slidingActuatorData.csv"), slidingActuatorData)
        # add_many(getRowsFromCsvFile("csv/rotaryActuatorData.csv"), rotaryActuatorData)
        # add_many(getRowsFromCsvFile("csv/notesMaster.csv"), notesMaster)
        # add_many(getRowsFromCsvFile("csv/positioner.csv"), positioner)
        # add_many(getRowsFromCsvFile("csv/limit_switch.csv"), limitSwitch)
        # add_many(getRowsFromCsvFile("csv/solenoid.csv"), solenoid)
        pass

# DATA_UPLOAD_BULK()
# with app.app_context():
    # data_delete(cvTable)
    # cv_upload(getRowsFromCsvFile("csv/cvtable.csv"))
    # deleteCVDuplicates()
    # pressure_temp_upload(getRowsFromCsvFile("csv/pressureTemp.csv"))
# data_upload(region_list, regionMaster)
    

if __name__ == "__main__":
    app.run(debug=True,port=5000)
