# To get running numbers for customer master
from flask import app
from models import ratingMaster


def full_format(i):
    # limit of first range is 26 letters (A-Z) times 999 numbers (001-999)
    if i < 26 * 999:
        c,n = divmod(i,999)   # quotient c is index of letter 0-25, remainder n is 0-998
        c = chr(ord('A') + c) # compute letter
        n += 1
        return f'{c}{n:03}'
    # After first range, second range is 26 letters times 26 letters * 99 numbers (01-99)
    elif i < 26*999 + 26*26*99:
        i -= 26*999               # remove first range offset
        cc,n = divmod(i,99)       # remainder n is 0-98, use quotient cc to compute two letters
        c1,c2 = divmod(cc,26)     # c1 is index of first letter, c2 is index of second letter
        c1 = chr(ord('A') + c1)   # compute first letter
        c2 = chr(ord('A') + c2)   # compute second letter
        n += 1
        return f'{c1}{c2}{n:02}'
    else:
        raise OverflowError(f'limit is {26*999+26*26*99}')
    


project_status_list = ['Dead', 'Live', 'Lost', 'Regret', 'Won']
purpose_list = ['Bid On', 'Budget', 'Example', 'Order To Place', 'Technical']
# length_unit_list = [{'id': 'inch', 'name': 'inch'}, {'id': 'm', 'name': 'm'}, {'id': 'mm', 'name': 'mm'},
#                     {'id': 'cm', 'name': 'cm'}]

# flowrate_unit_list = [{'id': 'm3/hr', 'name': 'm3/hr'}, {'id': 'scfh', 'name': 'scfh'},
#                         {'id': 'gpm', 'name': 'gpm'},
#                         {'id': 'lb/hr', 'name': 'lb/hr'}, {'id': 'kg/hr', 'name': 'kg/hr'}]

# pressure_unit_list = [{'id': 'bar', 'name': 'bar (a)'}, {'id': 'bar', 'name': 'bar (g)'},
#                         {'id': 'kpa', 'name': 'kPa (a)'}, {'id': 'kpa', 'name': 'kPa (g)'},
#                         {'id': 'mpa', 'name': 'MPa (a)'}, {'id': 'mpa', 'name': 'MPa (g)'},
#                         {'id': 'pa', 'name': 'Pa (a)'}, {'id': 'pa', 'name': 'Pa (g)'},
#                         {'id': 'inh20', 'name': 'in H2O (a)'}, {'id': 'inh20', 'name': 'in H2O (g)'},
#                         {'id': 'inhg', 'name': 'in Hg (a)'}, {'id': 'inhg', 'name': 'in Hg (g)'},
#                         {'id': 'kg/cm2', 'name': 'kg/cm2 (a)'}, {'id': 'kg/cm2', 'name': 'kg/cm2 (g)'},
#                         {'id': 'mmh20', 'name': 'm H2O (a)'}, {'id': 'mmh20', 'name': 'm H2O (g)'},
#                         {'id': 'mbar', 'name': 'mbar (a)'}, {'id': 'mbar', 'name': 'mbar (g)'},
#                         {'id': 'mmhg', 'name': 'mm Hg (a)'}, {'id': 'mmhg', 'name': 'mm Hg (g)'},
#                         {'id': 'psia', 'name': 'psi (g)'}, {'id': 'psia', 'name': 'psi (a)'}]

# temp_unit_list = [{'id': 'C', 'name': '°C'}, {'id': 'F', 'name': '°F'}, {'id': 'K', 'name': 'K'},
#                     {'id': 'R', 'name': 'R'}]


def reorder_list(element, list_):
    if type(list_) == list:
        list_.pop(list_.index(element))
        list_.insert(0, element)
        return list_
    elif type(list_) == dict:
        list__ = list(list_.keys())
        list__.pop(list__.index(element))
        list__.insert(0, element)
        return list__





def notes_dict_reorder(input_dict, company, address):
    print(f"{input_dict}")
    output_dict = {}
    key_list_ = list(input_dict.keys())
    key_list = reorder_list(company, key_list_)
    for keys_ in key_list:
        if keys_ == company:
            addresses_ = input_dict[keys_]
            address_reorder = reorder_list(address, addresses_)
            output_dict[keys_] = address_reorder
        else:
            output_dict[keys_] = input_dict[keys_]
    return output_dict

volume_unit_list = [{"id" : "inch3", "name": "inch3 "},{"id" : "m3", "name": "m3 "}]
temperature_unit_list = [{"id": "C", "name": "°C"}, {"id": "F", "name": "°F"}, {"id": "R", "name": "R"}, {"id": "K", "name": "K"}]
length_unit_list = [{'id': 'inch', 'name': 'inch'}, {'id': 'mm', 'name': 'mm'}]
pressure_unit_list = [{'id': 'bar (a)', 'name': 'bar (a)'}, {'id': 'bar (g)', 'name': 'bar (g)'},
                          {'id': 'kPa (a)', 'name': 'kPa (a)'}, {'id': 'kPa (g)', 'name': 'kPa (g)'},
                          {'id': 'MPa (a)', 'name': 'MPa (a)'}, {'id': 'MPa (g)', 'name': 'MPa (g)'},
                          {'id': 'pa (a)', 'name': 'Pa (a)'}, {'id': 'pa (g)', 'name': 'Pa (g)'},
                          {'id': 'inh20 (a)', 'name': 'in H2O (a)'}, {'id': 'inh20 (g)', 'name': 'in H2O (g)'},
                          {'id': 'inhg (a)', 'name': 'in Hg (a)'}, {'id': 'inhg (g)', 'name': 'in Hg (g)'},
                          {'id': 'kg/cm2 (a)', 'name': 'kg/cm2 (a)'}, {'id': 'kg/cm2 (g)', 'name': 'kg/cm2 (g)'},
                          {'id': 'mmh20 (a)', 'name': 'm H2O (a)'}, {'id': 'mmh20 (g)', 'name': 'm H2O (g)'},
                          {'id': 'mbar (a)', 'name': 'mbar (a)'}, {'id': 'mbar (g)', 'name': 'mbar (g)'},
                          {'id': 'mmhg (a)', 'name': 'mm Hg (a)'}, {'id': 'mmhg (g)', 'name': 'mm Hg (g)'},
                          {'id': 'psia (a)', 'name': 'psi (a)'}, {'id': 'psia (g)', 'name': 'psi (g)'},
                          {'id': 'atm (a)', 'name': 'atm (a)'}, {'id': 'atm (g)', 'name': 'atm (g)'},
                          {'id': 'torr (a)', 'name': 'torr (a)'}, {'id': 'torr (g)', 'name': 'torr (g)'}]

flowrate_unit_list = [{'id': 'm3/hr', 'name': 'm3/hr'},{'id':'m3/m', 'name':'m3/m'}, {'id': 'scfh', 'name': 'scfh'},
                      {'id': 'gpm', 'name': 'gpm'},{'id':'kg/s', 'name': 'kg/s'},{'id':'kg/m', 'name':'kg/m'},
                      {'id':'kg/hr', 'name':'kg/hr'}, {'id':'lb/s', 'name':'lb/s'},{'id':'lb/m','name':'lb/m'},{'id':'lb/hr','name':'lb/hr'}]

area_unit_list = [{'id': 'inch2', 'name': 'inch²'}, {'id': 'mm2', 'name': 'mm²'}]

del_p_unit_list = [{'id': 'bar', 'name': 'bar'},
                          {'id': 'kPa', 'name': 'kPa'},
                          {'id': 'MPa', 'name': 'MPa'}, 
                          {'id': 'pa', 'name': 'Pa'}, 
                          {'id': 'inh20', 'name': 'in H2O'}, 
                          {'id': 'inhg', 'name': 'in Hg'}, 
                          {'id': 'kg/cm2', 'name': 'kg/cm2'}, 
                          {'id': 'mmh20', 'name': 'm H2O'}, 
                          {'id': 'mbar', 'name': 'mbar'}, 
                          {'id': 'mmhg', 'name': 'mm Hg'}, 
                          {'id': 'psia', 'name': 'psi'}, 
                          {'id': 'atm', 'name': 'atm'}, 
                          {'id': 'torr', 'name': 'torr'}, ]

force_unit_list = [{'id': 'lbf', 'name': 'lbf'}, {'id': 'kgf', 'name': 'kgf'}, {'id': 'N', 'name': 'N'}]
torque_unit_list = [{'id': 'lbf.inch', 'name': 'lbf.inch'}, {'id':'kgf.m', 'name':'kgf.m'}, {'id':'N.m', 'name':'N.m'}]

pipe_schedule = ['select --','std', '10', '20', '30', '40', '80', '120', '160', 'xs', 'xxs']

pipe_shedule_list = [{"id": item, "name": item} for item in pipe_schedule]

units_dict = {"pressure": pressure_unit_list, "temperature": temperature_unit_list, 
              "flowrate": flowrate_unit_list, "length": length_unit_list, 
              "delPressure": del_p_unit_list, "pipe_schedule": pipe_shedule_list, 
              "area": area_unit_list, "force": force_unit_list, "volume":volume_unit_list,"torque":torque_unit_list}

# Unit Conversion Logic
def convert_L_SI(val, unit_in, unit_out, density):
    SI = {'mm': 0.001, 'cm': 0.01, 'm': 1.0, 'km': 1000.0, 'inch': 0.0254}
    return val * SI[unit_in] / SI[unit_out]


def conver_P_SI(val, unit_in, unit_out, density):
    print(f'unitINNNNNN {unit_in},{unit_out}')
    unit_in = unit_in.split(' ')
    unit_out = unit_out.split(' ')
    print(f'G_TO_AS {unit_in[0]},{unit_out[0]}')
    if unit_in[-1] == '(g)':
        val = meta_convert_g_to_a(float(val),unit_in[0])
        
    else:
        val = val
    
        
    

    print(f'INTERRVALUESGGGG {val},{unit_in[-1]},{unit_out[-1]}')
    SI = {'psia': 6894.76, 'kg/cm2': 98066.5, 'pa': 1, 'kPa': 1000, 'bar': 100000, 'MPa': 1000000,
          'inh20': 0.00401865, 'mmh20': 9.80665, 'inhg': 0.0002953, 'mmhg': 133.322, 'mbar': 0.01}
    final_val = val * SI[unit_in[0]] / SI[unit_out[0]]
    
    
    
    if unit_out[-1] == '(g)':
        return_val = meta_convert_a_to_g(final_val,unit_out[0])
    else:
        return_val = final_val 
    print(f'FINALVALUES {return_val}')
    
    return return_val




def convert_T_SI(val, unit_in, unit_out, density):
    def c_to_c(value):
        return value

    def c_to_f(value):
        return 1.8 * value + 32

    def c_to_k(value):
        return value + 273.15

    def c_to_r(value):
        return 1.8 * value + 491.67

    def f_to_c(value):
        return (value - 32) * (5 / 9)

    def k_to_c(value):
        return value - 273.15

    def r_to_c(value):
        return (value - 491.67) * (5 / 9)

    SI = {'F': c_to_f, 'K': c_to_k, 'R': c_to_r, 'C': c_to_c}
    SI_2 = {'F': f_to_c, 'K': k_to_c, 'R': r_to_c, 'C': c_to_c}

    # val_to_c = SI[unit_in](val)
    return SI[unit_out](SI_2[unit_in](val))

def mass_internalconv(val, unit_in, unit_out):
    SI = {'kg/hr': 1, 
          'lb/hr': 1 / 0.453592,  # 1 lb/hr = 0.453592 kg/hr
          'lb/m': 0.453592 * 60,  # 1 lb/m = 0.453592 / 60 kg/hr
          'kg/m': 60,  # 1 kg/m = 1 / 60 kg/hr
          'lb/s': 0.453592 * 3600,  # 1 lb/s = 0.453592 / 3600 kg/hr
          'kg/s': 3600  # 1 kg/s = 1 / 3600 kg/hr
         }

    return val * SI[unit_in] / SI[unit_out]
def conver_FR_SI(val, unit_in, unit_out, density):
    print(f'FLOWRATESI {val},{unit_in},{unit_out},{density}')
    massunits = ['kg/s','kg/m','lb/s','lb/m','lb/hr']
    if unit_in in massunits:
        val = mass_internalconv(val,unit_in,'kg/hr')
        unit_in = 'kg/hr'
    
    print(f'VALUESS {val},{unit_in}')
    SI = {'m3/hr': 1, 
          'm3/m': 1 / 60,
          'scfh': 1 / 35.31, 
          'gpm': 1 / 4.402868,  
          'kg/hr': 1 / density
         }
    
    if unit_out in massunits:
        val = val * SI[unit_in] / SI['kg/hr']
        result_ = mass_internalconv(val,'kg/hr',unit_out)
    else:
        result_ = val * SI[unit_in] / SI[unit_out]


    return result_
    

def convert_A_SI(val, unit_in, unit_out, density):
    SI = {'inch2': 1, 'mm2': 1 / 645.16}
    return val * SI[unit_in] / SI[unit_out]

def convert_F_SI(val, unit_in, unit_out, density):
    SI = {'lbf': 1, 'kgf': 1 / 0.453, 'N': 1 / 4.448}
    return val * SI[unit_in] / SI[unit_out]
def convert_V_SI(val, unit_in, unit_out, density):
    SI = {'inch3': 1, 'm3': 61020}
    return val * SI[unit_in] / SI[unit_out]

def convert_TOR_SI(val, unit_in, unit_out, density):
    SI = {'lbf.inch': 1, 'kgf.m':1 / 0.012, 'N.m': 1 / 0.1129}
    return val * SI[unit_in] / SI[unit_out]

def meta_convert_P_T_FR_L(prop, val, unit_in, unit_out, density):
    print(f'KLASDFF {prop},{type(val)},{type(unit_in)},{type(unit_out)}')
    properties = {"T": convert_T_SI, "P": conver_P_SI, "FR": conver_FR_SI, "L": convert_L_SI, 'A': convert_A_SI, 'F':convert_F_SI, 'V':convert_V_SI, 'TOR':convert_TOR_SI}
    return properties[prop](val, unit_in, unit_out, density)

def meta_convert_g_to_a(value, prop):
    properties = {"bar":1.01325 , "pa":100000, "kPa":101.284, "MPa":0.1, "psia":14.69, "kg/cm2":1.033,"torr":759.692,"atm":1,"mmh20":10328.092,"mmhg":759.692}
    return value + properties[prop]


def meta_convert_a_to_g(value,prop):
    properties = {"bar":1.01325 , "pa":100000, "kPa":101.284, "MPa":0.1, "psia":14.69, "kg/cm2":1.033, "torr":759.692,"atm":1,"mmh20":10328.092,"mmhg":759.692}
    return value - properties[prop]


def conver_FR_noise(val, unit_in):
    SI = {'m3/hr': 0.001, 'scfh': 0.049, 'gpm': 0.0060, 'lb/hr': 2.20462, 'kg/hr': 1}
    a = (val * SI[unit_in] / SI['kg/hr']) / 3600
    return a


N1 = {('m3/hr', 'kpa'): 0.0865, ('m3/hr', 'bar'): 0.865, ('gpm', 'psia'): 1}
N2 = {'mm': 0.00214, 'inch': 890}
N4 = {('m3/hr', 'mm'): 76000, ('gpm', 'inch'): 173000}


# FR values for 56-40000

REv = [56, 66, 79, 94, 110, 130, 154, 188, 230, 278, 340, 471, 620, 980, 1560, 2470, 4600, 10200, 40000]
FR = [0.284, 0.32, 0.36, 0.4, 0.44, 0.48, 0.52, 0.56, 0.6, 0.64, 0.68, 0.72, 0.76, 0.8, 0.84, 0.88, 0.92, 0.96, 1]

def getValveType(valveStyle):
    valve_dict = {'Globe Straight': 'globe', 'Globe Angle': 'globe', 'Butterfly Lugged Wafer': 'butterfly', 'Butterfly Double Flanged': 'butterfly'}
    return valve_dict[valveStyle]



# Constants
# todo = Constants
N5_mm = 0.00241  # in mm
N5_in = 1000
N6_kghr_kPa_kgm3 = 2.73
N6_kghr_bar_kgm3 = 27.3
N6_lbhr_psi_lbft3 = 63.3
N7_O_m3hr_kPa_C = 3.94  # input in Kelvin
N7_0_m3hr_bar_C = 394
N7_155_m3hr_kPa_C = 4.17
N7_155_m3hr_bar_C = 417
N7_60_scfh_psi_F = 1360  # input in R
N8_kghr_kPa_K = 0.498
N8_kghr_bar_K = 94.8
N8_lbhr_psi_K = 19.3
N9_O_m3hr_kPa_C = 21.2  # input in Kelvin
N9_0_m3hr_bar_C = 2120
N9_155_m3hr_kPa_C = 22.4
N9_155_m3hr_bar_C = 2240
N9_60_scfh_psi_F = 7320  # input in R

def getFlowCharacter(flowcharacter):
    flowcharact_dict = {'Equal %': 'equal', 'Linear': 'linear', 'Modified Equal %': 'equal'}
    return flowcharact_dict[flowcharacter]


actuator_type_dict = [
      {'id': 'Manual Gearbox', 'name': 'Manual Gearbox'},
      {'id': 'Spring & Diaphragm', 'name': 'Spring & Diaphragm'},
      {'id': 'Multi Spring & Diaphragm', 'name': 'Multi Spring & Diaphragm'},
      {'id': 'Piston with Spring', 'name': 'Piston with Spring'},
      {'id': 'Piston without Spring', 'name': 'Piston without Spring'},
      {'id': 'SY', 'name': 'Scotch Yoke'},
      {'id': 'SYC', 'name': 'Scotch Yoke-Canted'},
      {'id': 'SYCDA', 'name': 'Scotch Yoke-Canted Double Acting'},
      ]

fail_action_dict = [
      {'id': 'DA', 'name': 'Stay Put'},
      {'id': 'AFO', 'name': 'Fail Open'},
      {'id': 'AFC', 'name': 'Fail Close'}
      ]


hand_wheel_dict = [
      {'id': 'None', 'name': 'N/A'},
      {'id': 'Side Mounted', 'name': 'Side Mounted'},
      {'id': 'Top Mounted', 'name': 'Top Mounted'}
      ]


orientaton_dict = [
      {'id': 'None', 'name': 'N/A'},
      {'id': 'Horizontal', 'name': 'Horizontal'},
      {'id': 'Vertical', 'name': 'Vertical'}
      ]

adjustable_travel_stops_dict = [
      {'id': 'None', 'name': 'N/A'},
      {'id': 'Limit Open', 'name': 'Limit Open'},
      {'id': 'Limit Close', 'name': 'Limit Close'}
      ]


actuator_data_dict = {'actType': actuator_type_dict,
                      'failAction': fail_action_dict,
                      'handwheel': hand_wheel_dict, 
                      'orientation': orientaton_dict,
                      'travel': adjustable_travel_stops_dict
                      }



valve_force_dict = [{'key': ('contour', 'unbalanced', 'under', 'shutoff'), 'formula': 1},
                    {'key': ('cage', 'unbalanced', 'under', 'shutoff'), 'formula': 2},
                    {'key': ('cage', 'unbalanced', 'over', 'shutoff'), 'formula': 3},
                    {'key': ('cage', 'balanced', 'under', 'shutoff'), 'formula': 4},
                    {'key': ('cage', 'balanced', 'over', 'shutoff'), 'formula': 5},
                    {'key': ('contour', 'unbalanced', 'under', 'shutoff+'), 'formula': 6},
                    {'key': ('cage', 'unbalanced', 'under', 'shutoff+'), 'formula': 7},
                    {'key': ('cage', 'unbalanced', 'over', 'shutoff+'), 'formula': 8},
                    {'key': ('cage', 'balanced', 'under', 'shutoff+'), 'formula': 9},
                    {'key': ('cage', 'balanced', 'over', 'shutoff+'), 'formula': 10},
                    {'key': ('contour', 'unbalanced', 'under', 'close'), 'formula': 11},
                    {'key': ('cage', 'unbalanced', 'under', 'close'), 'formula': 12},
                    {'key': ('cage', 'unbalanced', 'over', 'close'), 'formula': 13},
                    {'key': ('cage', 'balanced', 'under', 'close'), 'formula': 14},
                    {'key': ('cage', 'balanced', 'over', 'close'), 'formula': 15},
                    {'key': ('contour', 'unbalanced', 'under', 'open'), 'formula': 16},
                    {'key': ('cage', 'unbalanced', 'under', 'open'), 'formula': 17},
                    {'key': ('cage', 'unbalanced', 'over', 'open'), 'formula': 18},
                    {'key': ('cage', 'balanced', 'under', 'open'), 'formula': 19},
                    {'key': ('cage', 'balanced', 'over', 'open'), 'formula': 20},
                    ]


valve_table_keys = [
  'id',
  'quantity',
  'tagNumber',
  'serialNumber',
  'shutOffDelP',
  'maxPressure',
  'maxTemp',
  'minTemp',
  'shutOffDelPUnit',
  'maxPressureUnit',
  'maxTempUnit',
  'minTempUnit',
  'bonnetExtDimension',
  'application',
  'itemId',
  'ratingId',
  'materialId',
  'designStandardId',
  'valveStyleId',
  'fluidStateId',
  'endConnectionId',
  'endFinishId',
  'bonnetTypeId',
  'packingTypeId',
  'trimTypeId',
  'flowCharacterId',
  'flowDirectionId',
  'seatLeakageClassId',
  'bonnetId',
  'nde1Id',
  'nde2Id',
  'shaftId',
  'discId',
  'seatId',
  'packingId',
  'balanceSealId',
  'studNutId',
  'gasketId',
  'cageId'
]


def getBooleanFromString(bString):
    if bString == 'False':
        return False
    elif bString == 'True':
        return True
    else:
        return None

