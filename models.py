from flask_login import UserMixin
from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, DateTime, Float, or_, \
    BigInteger  # DB Column Datatype
from sqlalchemy.orm import relationship, backref 
from dbsetup import db


# issues check
class newColumn(db.Model):
    __tablename__ = "newCol"

    id = Column(Integer, primary_key=True)  
    newRow = Column(Float)


class stemSize(db.Model):
    __tablename__ = "stemSize"

    id = Column(Integer, primary_key=True)  
    valveSize = Column(Float)
    stemDia = Column(String(10))

class unbalanceAreaTb(db.Model):
    __tablename__ = "unbalanceAreaTb" 

    id = Column(Integer, primary_key=True)
    seatDia = Column(Float)
    plugDia = Column(Float)
    Ua = Column(Float)

    trimTypeId = Column(Integer, ForeignKey("trimType.id"))
    trimType_ = relationship('trimType', back_populates='trimType_ua')

    leakageClassId = Column(Integer, ForeignKey("seatLeakageClass.id"))
    seatLeakageClass__ = relationship('seatLeakageClass', back_populates='leakage_ua')


class Test(db.Model):
    __tablename__ = "Test"
    id = Column(Integer, primary_key=True)
    name = Column(String(1000))
    desc = Column(String(1000))

class userMaster(UserMixin, db.Model):
    __tablename__ = "userMaster"

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'confirm_deleted_rows': False
    }

    id = Column(Integer, primary_key=True)
    name = Column(String(1000))
    password = Column(String(100))
    employeeId = Column(String(100))
    email = Column(String(100), unique=True)
    mobile = Column(String(100))
    fccUser = Column(Boolean)

    # relationships
    # TODO 1 - Project Master
    project = relationship("projectMaster", cascade="all,delete", back_populates="user")

    # relationship as child
    departmentId = Column(Integer, ForeignKey("departmentMaster.id"))
    department = relationship("departmentMaster", back_populates="user")

    designationId = Column(Integer, ForeignKey("designationMaster.id"))
    designation = relationship("designationMaster", back_populates="user")


class companyMaster(db.Model):
    __tablename__ = "companyMaster"

    __mapper_args__ = {
        'polymorphic_identity': 'company',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(300))
    description = Column(String(300))

    # relationship as parent
    address = relationship('addressMaster', cascade="all,delete",  back_populates='company')


class departmentMaster(db.Model):
    __tablename__ = "departmentMaster"

    __mapper_args__ = {
        'polymorphic_identity': 'department',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    user = relationship("userMaster", back_populates="department")


class designationMaster(db.Model):
    __tablename__ = "designationMaster"

    __mapper_args__ = {
        'polymorphic_identity': 'deisgnation',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    user = relationship("userMaster", back_populates="designation")


# data upload done
class industryMaster(db.Model):
    __tablename__ = "industryMaster"

    __mapper_args__ = {
        'polymorphic_identity': 'industry',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    # relationship as parent
    project = relationship("projectMaster", cascade="all,delete", back_populates="industry")

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = industryMaster.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()

# data upload done
class regionMaster(db.Model):
    __tablename__ = "regionMaster"

    __mapper_args__ = {
        'polymorphic_identity': 'region',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    # relationship as parent
    project = relationship("projectMaster", cascade="all,delete", back_populates="region")

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = regionMaster.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


class addressMaster(db.Model):
    __tablename__ = "addressMaster"

    __mapper_args__ = {
        'polymorphic_identity': 'address',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    address = Column(String(300))
    customerCode = Column(String(15))  # to add as A001 to A999 and B001 to B999 and so on.
    isActive = Column(Boolean)

    # relationship as parent
    # projectCompany = relationship('projectMaster',uselist=False, backref='address_company')
    # projectEnduser = relationship('projectMaster',uselist=False, backref='address_enduser')
    address_project = relationship('addressProject', cascade="all,delete", back_populates='address')

    # relationship as child
    companyId = Column(Integer, ForeignKey("companyMaster.id"))
    company = relationship("companyMaster", back_populates="address")


class addressProject(db.Model):
    __tablename__ = "addressProject"

    __mapper_args__ = {
        'polymorphic_identity': 'addressP',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    isCompany = Column(Boolean)

    # child to address
    addressId = Column(Integer, ForeignKey("addressMaster.id"))
    address = relationship("addressMaster", back_populates="address_project")

    # child to project
    projectId = Column(Integer, ForeignKey("projectMaster.id"))
    project = relationship("projectMaster", back_populates="project_address")


class engineerProject(db.Model):
    __tablename__ = "engineerProject"

    __mapper_args__ = {
        'polymorphic_identity': 'engineerP',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    isApplication = Column(Boolean)

    # child to address
    engineerId = Column(Integer, ForeignKey("engineerMaster.id"))
    engineer = relationship("engineerMaster", back_populates="engineer_project")

    # child to project
    projectId = Column(Integer, ForeignKey("projectMaster.id"))
    project = relationship("projectMaster", back_populates="project_engineer")


class engineerMaster(db.Model):
    __tablename__ = "engineerMaster"
    __mapper_args__ = {
        'polymorphic_identity': 'engineer',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(300))
    designation = Column(String(300))

    # relationship as parent
    engineer_project = relationship('engineerProject', cascade="all,delete", back_populates='engineer')
    # projectContract = relationship("projectMaster",uselist=False, backref="engineer_contract")
    # projectApplicaton = relationship("projectMaster",uselist=False, backref="engineer_application")
    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = engineerMaster.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()

class projectMaster(db.Model):
    __tablename__ = "projectMaster"

    __mapper_args__ = {
        'polymorphic_identity': 'project',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    projectId = Column(String(100))
    projectRef = Column(String(100))
    enquiryRef = Column(String(100))
    enquiryReceivedDate = Column(DateTime)
    receiptDate = Column(DateTime)
    bidDueDate = Column(DateTime)
    purpose = Column(String(100))
    custPoNo = Column(String(100))
    workOderNo = Column(String(100))
    revisionNo = Column(Integer)
    status = Column(String(100))
    pressureUnit = Column(String(50))
    flowrateUnit = Column(String(50))
    temperatureUnit = Column(String(50))
    lengthUnit = Column(String(50))
    # relationship as parent
    item = relationship("itemMaster", cascade="all,delete", back_populates="project")
    projectnotes = relationship('projectNotes', cascade="all,delete", back_populates='project')
    project_address = relationship('addressProject', cascade="all,delete", back_populates='project')
    project_engineer = relationship('engineerProject', cascade="all,delete", back_populates='project')

    # relationship as child
    # TODO - User
    createdById = Column(Integer, ForeignKey("userMaster.id"))
    user = relationship("userMaster", back_populates="project")
    # TODO - Industry
    IndustryId = Column(Integer, ForeignKey("industryMaster.id"))
    industry = relationship("industryMaster", back_populates="project")
    # TODO - Engineer contract
    regionID = Column(Integer, ForeignKey("regionMaster.id"))
    region = relationship("regionMaster", back_populates="project")

    # TODO - Address

    # def update(self, **kwargs):
    #     for key, value in kwargs.items():
    #         print(key, value)
    #         setattr(self, key, value)
    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = projectMaster.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


class projectNotes(db.Model):
    __tablename__ = "projectNotes"
    __mapper_args__ = {
        'polymorphic_identity': 'projectNote',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    notesNumber = Column(String(300))
    notes = Column(String(300))
    date = Column(DateTime)

    # relationship as child
    projectId = Column(Integer, ForeignKey("projectMaster.id"))
    project = relationship("projectMaster", back_populates="projectnotes")


class itemNotesData(db.Model):
    __tablename__ = "itemNotesData"
    __mapper_args__ = {
        'polymorphic_identity': 'itemNote',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    content = Column(String(300))
    notesNumber = Column(String(300))

    # rel as child to item
    itemId = Column(Integer, ForeignKey("itemMaster.id"))
    item = relationship('itemMaster', back_populates='notes')


class notesMaster(db.Model):
    __tablename__ = "notesMaster"
    __mapper_args__ = {
        'polymorphic_identity': 'note',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    notesNumber = Column(String(10))
    content = Column(String(300))


class itemMaster(db.Model):
    __tablename__ = "itemMaster"
    __mapper_args__ = {
        'polymorphic_identity': 'item',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    itemNumber = Column(Integer)
    alternate = Column(String(50))
    standardStatus = Column(Boolean)
    pipeDataStatus = Column(Boolean)

    flowrate_unit = Column(String(20))
    inpres_unit = Column(String(20))
    outpres_unit = Column(String(20))
    intemp_unit = Column(String(20))
    vaporpres_unit = Column(String(20))
    criticalpres_unit = Column(String(20))
    inpipe_unit = Column(String(20))
    outpipe_unit = Column(String(20))
    valvesize_unit = Column(String(20))

    # rel as parent
    case = relationship("caseMaster", cascade="all,delete", back_populates="item")

    # one-to-one relationship with valve, actuator and accessories, as parent
    valve = relationship("valveDetailsMaster", cascade="all,delete", back_populates="item")
    actuator = relationship("actuatorMaster", cascade="all,delete", back_populates="item")
    accessories = relationship("accessoriesData", cascade="all,delete", back_populates="item")
    notes = relationship("itemNotesData", cascade="all,delete", back_populates="item")

    # relationship as child
    projectID = Column(Integer, ForeignKey("projectMaster.id"))
    project = relationship("projectMaster", back_populates="item")


# data upload done
class fluidState(db.Model):
    __tablename__ = "fluidState"
    __mapper_args__ = {
        'polymorphic_identity': 'state',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(100))

    # relationship as parent
    valve = relationship('valveDetailsMaster', cascade="all,delete", back_populates='state')

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = fluidState.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


# data upload done
class designStandard(db.Model):
    __tablename__ = "designStandard"
    __mapper_args__ = {
        'polymorphic_identity': 'standard',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(100))

    # relationship as parent
    valve = relationship('valveDetailsMaster', cascade="all,delete", back_populates='design')

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = designStandard.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


# data upload done
class valveStyle(db.Model):
    __tablename__ = "valveStyle"
    __mapper_args__ = {
        'polymorphic_identity': 'style',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(100))

    # relationship as parent
    valve = relationship('valveDetailsMaster', cascade="all,delete", back_populates='style')
    cv = relationship('cvTable', cascade="all,delete", back_populates='style')
    shaft_ = relationship('shaft', cascade="all,delete", back_populates='style')
    disc_ = relationship('disc', cascade="all,delete", back_populates='style')
    seat_ = relationship('seat', cascade="all,delete", back_populates='style')
    packing_ = relationship('packing', cascade="all,delete", back_populates='style')
    trimtype_ = relationship('trimType', cascade="all,delete", back_populates='style')

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = valveStyle.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


# data upload done
class applicationMaster(db.Model):
    __tablename__ = "applicationMaster"
    __mapper_args__ = {
        'polymorphic_identity': 'application',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(100))

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = applicationMaster.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


# data upload done
class ratingMaster(db.Model):
    __tablename__ = "ratingMaster"
    __mapper_args__ = {
        'polymorphic_identity': 'rating',
        'confirm_deleted_rows': False
    }   
    id = Column(Integer, primary_key=True)
    name = Column(String(100))

    # relationship as parent
    valve = relationship('valveDetailsMaster', cascade="all,delete", back_populates='rating')
    pt = relationship('pressureTempRating', cascade="all,delete", back_populates='rating')
    cv = relationship('cvTable', cascade="all,delete", back_populates='rating_c')
    packingF = relationship('packingFriction', cascade="all,delete", back_populates='rating')
    torque = relationship("packingTorque", cascade="all,delete", back_populates='rating')
    rotaryAct = relationship("shaftRotary", back_populates='rating')

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = ratingMaster.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


# data upload done
class materialMaster(db.Model):
    __tablename__ = "materialMaster"
    __mapper_args__ = {
        'polymorphic_identity': 'material',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(100))

    # relationship as parent
    valve = relationship('valveDetailsMaster', cascade="all,delete", back_populates='material')
    pt = relationship('pressureTempRating', cascade="all,delete", back_populates='material')

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = materialMaster.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


# data upload done
class pressureTempRating(db.Model):
    __tablename__ = "pressureTempRating"
    __mapper_args__ = {
        'polymorphic_identity': 'pressureTemp',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    maxTemp = Column(Float)
    minTemp = Column(Float)
    pressure = Column(Float)

    # relationship as child
    materialId = Column(Integer, ForeignKey("materialMaster.id"))
    material = relationship("materialMaster", back_populates="pt")

    ratingId = Column(Integer, ForeignKey("ratingMaster.id"))
    rating = relationship("ratingMaster", back_populates="pt")

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = pressureTempRating.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


# Multiple static dropdown


class endConnection(db.Model):
    __tablename__ = "endConnection"
    __mapper_args__ = {
        'polymorphic_identity': 'endC',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    endConnection_ = relationship('valveDetailsMaster', cascade="all,delete", back_populates='endConnection__')

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = endConnection.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()

# 19
class endFinish(db.Model):
    __tablename__ = "endFinish"
    __mapper_args__ = {
        'polymorphic_identity': 'endF',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    endFinish_ = relationship('valveDetailsMaster', cascade="all,delete", back_populates='endFinish__')

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = endFinish.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


# 20
class bonnetType(db.Model):
    __tablename__ = "bonnetType"
    __mapper_args__ = {
        'polymorphic_identity': 'bonnetTyp',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    bonnetType_ = relationship('valveDetailsMaster', cascade="all,delete", back_populates='bonnetType__')

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = bonnetType.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


# 21
class packingType(db.Model):
    __tablename__ = "packingType"
    __mapper_args__ = {
        'polymorphic_identity': 'packingTyp',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(300))
     
    packingType_ = relationship('valveDetailsMaster', cascade="all,delete", back_populates='packingType__')
    # packingT = relationship('packingFriction', cascade="all,delete", back_populates='packingType_')
    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = packingType.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


class trimType(db.Model):
    __tablename__ = "trimType"
    __mapper_args__ = {
        'polymorphic_identity': 'trim',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    trimType_ = relationship('valveDetailsMaster', cascade="all,delete", back_populates='trimType__')
    trimType_c = relationship('cvTable', cascade="all,delete", back_populates='trimType_')
    trimType_ua = relationship('unbalanceAreaTb', back_populates='trimType_')
    seatLoad = relationship('seatLoadForce', cascade="all,delete", back_populates='trimType_')
    kn = relationship("knValue", cascade="all,delete", back_populates="trimType_")
    actuatorCase = relationship('actuatorCaseData',back_populates='trimType_')

    valveStyleId = Column(Integer, ForeignKey("valveStyle.id"))
    style = relationship('valveStyle', back_populates='trimtype_')

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = trimType.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()

class flowCharacter(db.Model):  # TODO - Paandi  ............Done
    __tablename__ = "flowCharacter"
    __mapper_args__ = {
        'polymorphic_identity': 'flowC',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    flowCharacter_ = relationship('valveDetailsMaster', cascade="all,delete", back_populates='flowCharacter__')
    flowCharacter_c = relationship('cvTable', cascade="all,delete", back_populates='flowCharacter_')
    kn = relationship('knValue', cascade="all,delete", back_populates='flowCharacter_')

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = flowCharacter.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


# 23
class flowDirection(db.Model):  # TODO - Paandi  ............Done
    __tablename__ = "flowDirection"
    __mapper_args__ = {
        'polymorphic_identity': 'flowD',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    flowDirection_ = relationship('valveDetailsMaster', cascade="all,delete", back_populates='flowDirection__')
    flowDirection_c = relationship('cvTable', cascade="all,delete", back_populates='flowDirection_')
    actuatorCase = relationship('actuatorCaseData',back_populates='flowDirection_')
    
    kn = relationship('knValue', cascade="all,delete", back_populates='flowDirection_')

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = flowDirection.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


# 24
class seatLeakageClass(db.Model):  # TODO - Paandi    ..........Done
    __tablename__ = "seatLeakageClass"
    __mapper_args__ = {
        'polymorphic_identity': 'leakage',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(300))
    leakage_ua = relationship('unbalanceAreaTb', back_populates='seatLeakageClass__')
    seatLeakageClass_ = relationship('valveDetailsMaster', cascade="all,delete", back_populates='seatLeakageClass__')
    seatLoad = relationship('seatLoadForce', cascade="all,delete", back_populates='leakage')

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = seatLeakageClass.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


# 25
class bonnet(db.Model):
    __tablename__ = "bonnet"
    __mapper_args__ = {
        'polymorphic_identity': 'bonne',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    bonnet_ = relationship('valveDetailsMaster', cascade="all,delete", back_populates='bonnet__')

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = bonnet.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            # print(key)
            # print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


class nde1(db.Model):
    __tablename__ = "nde1"
    __mapper_args__ = {
        'polymorphic_identity': 'nde',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    nde1_ = relationship('valveDetailsMaster', cascade="all,delete", back_populates='nde1__')


class nde2(db.Model):
    __tablename__ = "nde2"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    nde2_ = relationship('valveDetailsMaster', cascade="all,delete", back_populates='nde2__')



class shaftRotary(db.Model):
    __tablename__ = "shaftRotary"

    id = Column(Integer, primary_key=True)

    ratingId = Column(Integer, ForeignKey("ratingMaster.id"))
    rating = relationship("ratingMaster", back_populates="rotaryAct")

    valveSize = Column(Float)
    stemDia = Column(String(10))
    valveInterface = Column(String(10))


class shaft(db.Model):  # Stem in globe
    __tablename__ = "shaft"
    __mapper_args__ = {
        'polymorphic_identity': 'shaf',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    yield_strength = Column(Float)

    shaft_ = relationship('valveDetailsMaster', cascade="all,delete", back_populates='shaft__')

    valveStyleId = Column(Integer, ForeignKey("valveStyle.id"))
    style = relationship('valveStyle', back_populates='shaft_')

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = shaft.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


class disc(db.Model):  # plug in globe
    __tablename__ = "disc"
    __mapper_args__ = {
        'polymorphic_identity': 'dis',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(100))

    disc_ = relationship('valveDetailsMaster', cascade="all,delete", back_populates='disc__')

    valveStyleId = Column(Integer, ForeignKey("valveStyle.id"))
    style = relationship('valveStyle', back_populates='disc_')


class seat(db.Model):  # both seat
    __tablename__ = "seat"
    __mapper_args__ = {
        'polymorphic_identity': 'sea',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(100))

    seat_ = relationship('valveDetailsMaster', cascade="all,delete", back_populates='seat__')

    valveStyleId = Column(Integer, ForeignKey("valveStyle.id"))
    style = relationship('valveStyle', back_populates='seat_')

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = seat.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


class packing(db.Model):
    __tablename__ = "packing"
    __mapper_args__ = {
        'polymorphic_identity': 'pack',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(100))

    packing_ = relationship('valveDetailsMaster', cascade="all,delete", back_populates='packing__')
    packingF = relationship('packingFriction', cascade="all,delete", back_populates='packing_')

    valveStyleId = Column(Integer, ForeignKey("valveStyle.id"))
    style = relationship('valveStyle', back_populates='packing_')

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = packing.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


class balanceSeal(db.Model):  # NDE  # TODO - Paandi
    __tablename__ = "balanceSeal"
    __mapper_args__ = {
        'polymorphic_identity': 'balanceSel',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    balanceSeal_ = relationship('valveDetailsMaster', cascade="all,delete", back_populates='balanceSeal__')

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = balanceSeal.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


class studNut(db.Model):  # NDE  # TODO - Paandi
    __tablename__ = "studNut"
    __mapper_args__ = {
        'polymorphic_identity': 'stud',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    studNut_ = relationship('valveDetailsMaster', cascade="all,delete", back_populates='studNut__')


class gasket(db.Model):
    __tablename__ = "gasket"
    __mapper_args__ = {
        'polymorphic_identity': 'gas',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    gasket_ = relationship('valveDetailsMaster', cascade="all,delete", back_populates='gasket__')

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = gasket.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


class cageClamp(db.Model):
    __tablename__ = "cageClamp"
    __mapper_args__ = {
        'polymorphic_identity': 'cage',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    cage_ = relationship('valveDetailsMaster', cascade="all,delete", back_populates='cage__')


# To cv table
class balancing(db.Model):
    __tablename__ = "balancing"
    __mapper_args__ = {
        'polymorphic_identity': 'balance',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    balancing_ = relationship('valveDetailsMaster', cascade="all,delete", back_populates='balancing__')

    balancing_c = relationship('cvTable', cascade="all,delete", back_populates='balancing_')
    actuatorCase = relationship('actuatorCaseData',back_populates='balancing_')

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = balancing.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


# TODO dropdowns end

class valveDetailsMaster(db.Model):
    __tablename__ = "valveDetailsMaster"
    __mapper_args__ = {
        'polymorphic_identity': 'valveData',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    quantity = Column(Integer)
    tagNumber = Column(String(150))
    serialNumber = Column(String(50))
    shutOffDelP = Column(Float)
    maxPressure = Column(Float)
    maxTemp = Column(Float)
    minTemp = Column(Float)
    shutOffDelPUnit = Column(String(50))
    maxPressureUnit = Column(String(50))
    maxTempUnit = Column(String(50))
    minTempUnit = Column(String(50))
    bonnetExtDimension = Column(Float)
    application = Column(String(150))

    # one-to-one relationship with itemMaser
    itemId = Column(Integer, ForeignKey("itemMaster.id"))
    item = relationship("itemMaster", back_populates="valve")

    # rel as child individual
    ratingId = Column(Integer, ForeignKey("ratingMaster.id"))
    rating = relationship("ratingMaster", back_populates="valve")

    materialId = Column(Integer, ForeignKey("materialMaster.id"))
    material = relationship("materialMaster", back_populates="valve")

    designStandardId = Column(Integer, ForeignKey("designStandard.id"))
    design = relationship("designStandard", back_populates="valve")

    valveStyleId = Column(Integer, ForeignKey("valveStyle.id"))
    style = relationship("valveStyle", back_populates="valve")

    fluidStateId = Column(Integer, ForeignKey("fluidState.id"))
    state = relationship("fluidState", back_populates="valve")

    fluidPropertiesId = Column(Integer, ForeignKey("fluidProperties.id"))
    fluidproperties = relationship("fluidProperties", back_populates="valve")

    # rel as child dropdown
    endConnectionId = Column(Integer, ForeignKey("endConnection.id"))
    endConnection__ = relationship('endConnection', back_populates='endConnection_')

    endFinishId = Column(Integer, ForeignKey("endFinish.id"))
    endFinish__ = relationship('endFinish', back_populates='endFinish_')

    bonnetTypeId = Column(Integer, ForeignKey("bonnetType.id"))
    bonnetType__ = relationship('bonnetType', back_populates='bonnetType_')

    packingTypeId = Column(Integer, ForeignKey("packingType.id"))
    packingType__ = relationship('packingType', back_populates='packingType_')

    trimTypeId = Column(Integer, ForeignKey("trimType.id"))
    trimType__ = relationship('trimType', back_populates='trimType_')

    flowCharacterId = Column(Integer, ForeignKey("flowCharacter.id"))
    flowCharacter__ = relationship('flowCharacter', back_populates='flowCharacter_')

    flowDirectionId = Column(Integer, ForeignKey("flowDirection.id"))
    flowDirection__ = relationship('flowDirection', back_populates='flowDirection_')

    seatLeakageClassId = Column(Integer, ForeignKey("seatLeakageClass.id"))
    seatLeakageClass__ = relationship('seatLeakageClass', back_populates='seatLeakageClass_')

    bonnetId = Column(Integer, ForeignKey("bonnet.id"))
    bonnet__ = relationship('bonnet', back_populates='bonnet_')

    nde1Id = Column(Integer, ForeignKey("nde1.id"))
    nde1__ = relationship('nde1', back_populates='nde1_')

    nde2Id = Column(Integer, ForeignKey("nde2.id"))
    nde2__ = relationship('nde2', back_populates='nde2_')

    shaftId = Column(Integer, ForeignKey("shaft.id"))
    shaft__ = relationship('shaft', back_populates='shaft_')

    discId = Column(Integer, ForeignKey("disc.id"))
    disc__ = relationship('disc', back_populates='disc_')

    seatId = Column(Integer, ForeignKey("seat.id"))
    seat__ = relationship('seat', back_populates='seat_')

    packingId = Column(Integer, ForeignKey("packing.id"))
    packing__ = relationship('packing', back_populates='packing_')

    balancingId = Column(Integer, ForeignKey("balancing.id"))
    balancing__ = relationship('balancing', back_populates='balancing_')

    balanceSealId = Column(Integer, ForeignKey("balanceSeal.id"))
    balanceSeal__ = relationship('balanceSeal', back_populates='balanceSeal_')

    studNutId = Column(Integer, ForeignKey("studNut.id"))
    studNut__ = relationship('studNut', back_populates='studNut_')

    gasketId = Column(Integer, ForeignKey("gasket.id"))
    gasket__ = relationship('gasket', back_populates='gasket_')

    cageId = Column(Integer, ForeignKey("cageClamp.id"))
    cage__ = relationship('cageClamp', back_populates='cage_')

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = valveDetailsMaster.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            # print(key)
            # print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


class pipeArea(db.Model):
    __tablename__ = "pipeArea"
    __mapper_args__ = {
        'polymorphic_identity': 'pipeAre',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    nominalDia = Column(Float)
    nominalPipeSize = Column(Float)
    outerDia = Column(Float)
    thickness = Column(Float)
    area = Column(Float)
    schedule = Column(String(50))

    # rel as parent
    caseI = relationship("caseMaster", cascade="all,delete", back_populates="iPipe")
    # caseO = relationship("caseMaster", back_populates="oPipe")

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = pipeArea.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


class cvTable(db.Model):
    __tablename__ = "cvTable"
    __mapper_args__ = {
        'polymorphic_identity': 'cvT',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    # valveStyleId = Column(Integer)
    valveSize = Column(Float)
    series = Column(String(50))

    # rel as parent
    value = relationship("cvValues", cascade="all,delete", back_populates="cv")
    case = relationship("caseMaster", cascade="all,delete", back_populates="cv")
    torque = relationship("packingTorque", cascade="all,delete", back_populates="cv")

    # rel as child

    trimTypeId = Column(Integer, ForeignKey("trimType.id"))
    trimType_ = relationship('trimType', back_populates='trimType_c')

    flowCharacId = Column(Integer, ForeignKey("flowCharacter.id"))
    flowCharacter_ = relationship('flowCharacter', back_populates='flowCharacter_c')

    flowDirId = Column(Integer, ForeignKey("flowDirection.id"))
    flowDirection_ = relationship('flowDirection', back_populates='flowDirection_c')

    balancingId = Column(Integer, ForeignKey("balancing.id"))
    balancing_ = relationship('balancing', back_populates='balancing_c')

    ratingId = Column(Integer, ForeignKey("ratingMaster.id"))
    rating_c = relationship('ratingMaster', back_populates='cv')

    valveStyleId = Column(Integer, ForeignKey("valveStyle.id"))
    style = relationship('valveStyle', back_populates='cv')


class cvValues(db.Model):
    __tablename__ = "cvValues"
    __mapper_args__ = {
        'polymorphic_identity': 'cvV',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    coeff = Column(String(50))
    one = Column(Float)
    two = Column(Float)
    three = Column(Float)
    four = Column(Float)
    five = Column(Float)
    six = Column(Float)
    seven = Column(Float)
    eight = Column(Float)
    nine = Column(Float)
    ten = Column(Float)

    seatBore = Column(Float)  # taken as discDia for butterfly
    travel = Column(Float)  # taken as rotation for butterfly

    # rel as child
    cvId = Column(Integer, ForeignKey("cvTable.id"))
    cv = relationship('cvTable', back_populates='value')


class fluidProperties(db.Model):
    __tablename__ = "fluidProperties"
    __mapper_args__ = {
        'polymorphic_identity': 'fluidP',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    fluidState = Column(String(100))
    fluidName = Column(String(100))
    specificGravity = Column(Float)
    vaporPressure = Column(Float)
    viscosity = Column(Float)
    criticalPressure = Column(Float)
    molecularWeight = Column(Float)
    specificHeatRatio = Column(Float)
    compressibilityFactor = Column(Float)

    # rel as parent
    case = relationship("caseMaster", cascade="all,delete", back_populates="fluid")

    valve = relationship('valveDetailsMaster', cascade="all,delete", back_populates='fluidproperties')

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = fluidProperties.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


class caseMaster(db.Model):
    __tablename__ = "caseMaster"
    __mapper_args__ = {
        'polymorphic_identity': 'case',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    flowrate = Column(Float)
    inletPressure = Column(Float)
    outletPressure = Column(Float)
    inletTemp = Column(Float)
    vaporPressure = Column(Float)
    specificGravity = Column(Float)
    kinematicViscosity = Column(Float)
    fl = Column(Float)
    calculatedCv = Column(Float)
    openingPercentage = Column(Float)
    chokedDrop = Column(Float)
    Ff = Column(Float)
    Fp = Column(Float)
    Flp = Column(Float)
    kc = Column(Float)
    ar = Column(Float)
    spl = Column(Float)
    reNumber = Column(Float)
    pipeInVel = Column(Float)
    pipeOutVel = Column(Float)
    valveVel = Column(Float)
    tex = Column(Float)
    powerLevel = Column(Float)
    requiredStages = Column(Float)
    specificHeatRatio = Column(Float)
    mw_sg = Column(String(50))
    molecularWeight = Column(Float)
    compressibility = Column(Float)
    x_delp = Column(Float)
    fk = Column(Float)
    y_expansion = Column(Float)
    xt = Column(Float)
    xtp = Column(Float)
    fd = Column(Float)
    machNoUp = Column(Float)
    machNoDown = Column(Float)
    machNoValve = Column(Float)
    sonicVelUp = Column(Float)
    sonicVelDown = Column(Float)
    sonicVelValve = Column(Float)
    outletDensity = Column(Float)
    criticalPressure = Column(Float)
    inletPipeSize = Column(Float)
    outletPipeSize = Column(Float)
    valveSize = Column(Float)
    seatDia = Column(Float)
    ratedCv = Column(Float)

    # rel as child
    inletPipeSchId = Column(Integer, ForeignKey("pipeArea.id"))
    iPipe = relationship('pipeArea', back_populates='caseI', foreign_keys="[caseMaster.inletPipeSchId]")

    # outletPipeSchId = Column(Integer, ForeignKey("pipeArea.id"))
    # oPipe = relationship('pipeArea', back_populates='caseO', foreign_keys="[caseMaster.outletPipeSchId]")

    valveDiaId = Column(Integer, ForeignKey("cvTable.id"))
    cv = relationship('cvTable', back_populates='case')

    itemId = Column(Integer, ForeignKey("itemMaster.id"))
    item = relationship('itemMaster', back_populates='case')

    fluidId = Column(Integer, ForeignKey("fluidProperties.id"))
    fluid = relationship('fluidProperties', back_populates='case')

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = caseMaster.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}']".format(key))
        db.session.commit()


class actuatorMaster(db.Model):
    __tablename__ = "actuatorMaster"
    __mapper_args__ = {
        'polymorphic_identity': 'actuator',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    actuatorType = Column(String(100))
    springAction = Column(String(100))  # Fail Action
    handWheel = Column(String(100))
    adjustableTravelStop = Column(String(100))
    orientation = Column(String(100))
    availableAirSupplyMin = Column(Float)
    availableAirSupplyMax = Column(Float)
    availableAirSupplyMaxUnit = Column(String(20))
    travelStops = Column(String(100))
    setPressure = Column(Float)
    setPressureUnit = Column(String(20))


    # rel as parent
    actCase = relationship('actuatorCaseData', cascade="all,delete", back_populates='actuator_')
    rotCase = relationship('rotaryCaseData', cascade="all,delete", back_populates='actuator_')

    # rel as child to item
    itemId = Column(Integer, ForeignKey("itemMaster.id"))
    item = relationship('itemMaster', back_populates='actuator')

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = actuatorMaster.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()



class slidingActuatorData(db.Model):
    __mapper_args__ = {
        'polymorphic_identity': 'slidingAct',
        'confirm_deleted_rows': False
    }
    __tablename__ = "slidingActuatorData"
    id = Column(Integer, primary_key=True)
    actType = Column(String(100))
    failAction = Column(String(100))
    stemDia = Column(Float)
    yokeBossDia = Column(Float)
    actSize = Column(String(100))
    effectiveArea = Column(Float)
    travel = Column(Float)
    sMin = Column(Float)
    sMax = Column(Float)
    springRate = Column(Float)
    VO = Column(Float)
    VM = Column(Float)

    # rel as parent
    actuatorCase = relationship('actuatorCaseData', cascade="all,delete", back_populates='slidingActuator')


class rotaryActuatorData(db.Model):
    __tablename__ = "rotaryActuatorData"
    __mapper_args__ = {
        'polymorphic_identity': 'rotAct',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    actType = Column(String(100))
    failAction = Column(String(100))
    valveInterface = Column(String(100))
    actSize_ = Column(String(100))
    actSize = Column(Float)
    springSet = Column(String(100))
    torqueType = Column(String(100))
    setPressure = Column(String(100))
    start = Column(Float)
    mid = Column(Float)
    end = Column(Float)

    # rel as parent
    actuatorCase = relationship('actuatorCaseData', cascade="all,delete", back_populates='rotaryActuator')

class strokeCase(db.Model):
    __tablename__ = "strokeCase"
    
    #input
    id = Column(Integer, primary_key=True) 
    act_size = Column(Float)
    act_travel = Column(Float)
    diaphragm_ea = Column(Float)
    lower_benchset = Column(Float)
    upper_benchset = Column(Float)
    spring_rate = Column(Float)
    airsupply_max = Column(Float)
    clearance_vol = Column(Float)
    swept_vol = Column(Float) 

    diaphragm_eaUnit = Column(String(20))
    lower_benchsetUnit = Column(String(20))
    upper_benchsetUnit = Column(String(20))
    spring_rateUnit = Column(String(20))
    airsupply_maxUnit = Column(String(20))
    clearance_volUnit = Column(String(20))
    swept_volUnit = Column(String(20))
    act_travelUnit = Column(String(20))

    #intermediate results
    piExhaust = Column(Float)
    pfExhaust = Column(Float)
    piFill = Column(Float)
    pfFill = Column(Float)
    combinedCVFill = Column(Float)
    combinedCVExhaust = Column(Float)

    piExhaustUnit = Column(String(20))
    pfExhaustUnit = Column(String(20))
    piFillUnit = Column(String(20))
    pfFillUnit = Column(String(20))

    #final results 
    prefillTime = Column(Float) 
    totalfillTime = Column(Float) 
    preExhaustTime = Column(Float) 
    totalExhaustTime = Column(Float) 

    preFillUnit = Column(String(20))
    totalFillUnit = Column(String(20))
    preExhaustUnit = Column(String(20))
    totalExhaustUnit = Column(String(20))


    
    actuatorCaseId = Column(Integer, ForeignKey('actuatorCaseData.id'))
    actuatorCase_ = relationship('actuatorCaseData', back_populates='strokeCase_')

    status = Column(Integer)



    @staticmethod
    def update(new_data, id):
        print(f'NEWDATA {new_data}')
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = strokeCase.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(f'IM KEYS {key}')
            print(new_data[key])
            value = new_data[key] if new_data[key] else None  
            setattr(files, key, value)
        db.session.commit()

    
    

class rotaryCaseData(db.Model):
    __tablename__ = "rotaryCaseData"

    id = Column(Integer, primary_key=True) 

    #inputs
    v_size = Column(Float)
    disc_dia = Column(Float)
    shaft_dia = Column(Float)
    max_rot = Column(Float)
    delP = Column(Float)
    bush_coeff = Column(Float)
    csc = Column(Float)
    csv = Column(Float)
    a_factor = Column(Float)
    b_factor = Column(Float)
    pack_coeff = Column(Float)
    radial_coeff = Column(Float)
    Section = Column(Float)

    #units 
    valveSizeUnit = Column(String(100))
    discDiaUnit = Column(String(100))
    shaftDiaUnit = Column(String(100))
    max_rotUnit = Column(String(100))
    delpUnit = Column(String(100))
    packingRadialUnit = Column(String(100))

    #outputs 
    st = Column(Float)
    pt = Column(Float)
    ft = Column(Float)
    bto = Column(Float)
    rto = Column(Float)
    eto = Column(Float)
    btc = Column(Float)
    rtc = Column(Float)
    etc = Column(Float)
    mast = Column(Float)
    setP = Column(Float)
    actSize_ = Column(String(100))
    maxAir = Column(Float)
    springSet = Column(String(100))
    springSt = Column(String(100))
    springMd = Column(String(100))
    springEd = Column(String(100))
    AirSt = Column(String(100))
    AirMd = Column(String(100))
    AirEd = Column(String(100))
    ReqHand = Column(Float)

    #units 
    stUnit = Column(String(100))
    ptUnit = Column(String(100))
    ftUnit = Column(String(100))
    btoUnit = Column(String(100))
    rtoUnit = Column(String(100))
    etoUnit = Column(String(100))
    btcUnit = Column(String(100))
    rtcUnit = Column(String(100))
    etcUnit = Column(String(100))
    mastUnit = Column(String(100))
    setPUnit = Column(String(100))
    maxAirUnit = Column(String(100))
    stStartUnit = Column(String(100))
    stMidUnit = Column(String(100))
    stEndUnit = Column(String(100))
    atStartUnit = Column(String(100))
    atMidUnit = Column(String(100))
    atEndUnit = Column(String(100))
    handWheelUnit = Column(String(100))


    actuatorMasterId = Column(Integer, ForeignKey('actuatorMaster.id'))
    actuator_ = relationship('actuatorMaster', back_populates='rotCase')

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = rotaryCaseData.query.filter_by(id=id).first()  # files is the record
        # you want to update
        if files:
            for key, value in new_data.items():
                # Check if the value is empty (assuming empty strings are considered empty)
                if value[0] == "":
                    # Set the attribute to None (NULL) if the value is empty
                    setattr(files, key, None)
                else:
                    # Set the attribute to the value from the JSON
                    setattr(files, key, value[0])
            
            db.session.commit()
        else:
            # Handle the case where the record with the given ID is not found
            print("Record not found")


    











class actuatorCaseData(db.Model):
    __tablename__ = "actuatorCaseData"
    __mapper_args__ = {
        'polymorphic_identity': 'actCase',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)

    valveSize = Column(Float)
    seatDia = Column(Float)
    valveTravel = Column(Float)
    iPressure = Column(Float)
    oPressure = Column(Float)
    # sliding
    balancing = Column(String(100))
    unbalanceArea = Column(Float)
    stemDia = Column(Float)
    plugDia = Column(Float)
    unbalanceForce = Column(Float)
    fluidNeg = Column(Float)
    valveThrustClose = Column(Float)
    valveThrustOpen = Column(Float)
    shutOffForce = Column(Float)
    stemArea = Column(Float)
    springWindUp = Column(Float)
    maxSpringLoad = Column(Float)
    setPressure = Column(Float)
    sfMin = Column(Float)
    natMin = Column(Float)
    frictionBand = Column(Float)
    reqHandwheelThrust = Column(Float)
    thrust = Column(Float)
    act_size = Column(Float)
    act_travel = Column(Float)
    diaphragm_ea = Column(Float)
    lower_benchset = Column(Float)
    upper_benchset = Column(Float)
    spring_rate = Column(Float)
    airsupply_min = Column(Float) 
    airsupply_max = Column(Float)
    knValue = Column(Float)
    packingFriction = Column(Float)
    seatloadFactor = Column(Float)
    shutOffDelP = Column(Float)
    unbalForce = Column(Float) 
    negGrad = Column(Float)
    act_VO = Column(Float)



  

    # rotary
    # bushingCoeff = Column(Float)
    # packingFrictionCoeff = Column(Float)
    # aFactor = Column(Float)
    # bFactor = Column(Float)
    # packingRadialAxialStress = Column(Float)
    # packingSection = Column(Float)
    # seatingTorqueCalc = Column(Float)
    # packingTorqueCalc = Column(Float)
    # frictionTorqueCalc = Column(Float)
    # bto = Column(Float)
    # rto = Column(Float)
    # eto = Column(Float)
    # btc = Column(Float)
    # rtc = Column(Float)
    # etc = Column(Float)
    # mast = Column(Float)
    # setPressureR = Column(Float)
    # reqHandTorque = Column(Float)

    
    # Units
    valveSizeUnit = Column(String(20))
    seatDiaUnit = Column(String(20))
    unbalanceAreaUnit = Column(String(20))
    stemDiaUnit = Column(String(20))
    plugDiaUnit = Column(String(20))
    valveTravelUnit = Column(String(20))
    packingFrictionUnit = Column(String(20))
    inletPressureUnit = Column(String(20))
    outletPressureUnit = Column(String(20))
    delPShutoffUnit = Column(String(20))
    unbalForceOpenUnit = Column(String(20))
    negativeGradientUnit = Column(String(20))
    delPFlowingUnit = Column(String(20))

    # Output Units
    valveThrustCloseUnit = Column(String(20))
    valveThrustOpenUnit = Column(String(20))
    shutOffForceUnit = Column(String(20))
    stemAreaUnit = Column(String(20))
    actuatorTravelUnit = Column(String(20))
    effectiveAreaUnit = Column(String(20))
    lowerBenchsetUnit = Column(String(20))
    upperBenchSetUnit = Column(String(20))
    springRateUnit = Column(String(20))
    springWindupUnit = Column(String(20))
    maximumSpringLoadUnit = Column(String(20))
    maximumAirSupplyUnit = Column(String(20))
    setPressureUnit = Column(String(20))
    actuatorThrustValveCloseUnit = Column(String(20))
    actuatorThrustValveOpenUnit = Column(String(20))
    frictionBandUnit = Column(String(20))
    reqHandwheelUnit = Column(String(20))
    hwThrustUnit = Column(String(20))


    trimTypeId = Column(Integer, ForeignKey("trimType.id"))
    trimType_ = relationship('trimType', back_populates='actuatorCase')

    balancingId = Column(Integer, ForeignKey("balancing.id"))
    balancing_ = relationship('balancing', back_populates='actuatorCase')

    flowDirectionId = Column(Integer, ForeignKey("flowDirection.id"))
    flowDirection_ = relationship('flowDirection', back_populates='actuatorCase')


   

    # rel as child
    actuatorMasterId = Column(Integer, ForeignKey('actuatorMaster.id'))
    actuator_ = relationship('actuatorMaster', back_populates='actCase')

    packingFrictionId = Column(Integer, ForeignKey("packingFriction.id"))
    packingF = relationship('packingFriction', back_populates='actuatorCase')

    packingTorqueId = Column(Integer, ForeignKey("packingTorque.id"))
    packingT = relationship('packingTorque', back_populates='actuatorCase')

    seatLoadId = Column(Integer, ForeignKey("seatLoadForce.id"))
    seatLoad = relationship('seatLoadForce', back_populates='actuatorCase')

    slidingActuatorId = Column(Integer, ForeignKey("slidingActuatorData.id"))
    slidingActuator = relationship('slidingActuatorData', back_populates='actuatorCase')

    rotaryActuatorId = Column(Integer, ForeignKey("rotaryActuatorData.id"))
    rotaryActuator = relationship('rotaryActuatorData', back_populates='actuatorCase')


    strokeCase_ = relationship('strokeCase', back_populates='actuatorCase_')

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = actuatorCaseData.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()
    
    @staticmethod
    def delete(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = actuatorCaseData.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()

class yieldStrength(db.Model):
    __tablename__ = "yieldStrength"

    id = Column(Integer, primary_key=True)
    shaft_material = Column(String(200))
    yield_strength = Column(String(200))




class packingFriction(db.Model):
    __tablename__ = "packingFriction"
    __mapper_args__ = {
        'polymorphic_identity': 'packingF',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    stemDia = Column(Float)
    value = Column(Float)

    # rel as child
    ratingId = Column(Integer, ForeignKey("ratingMaster.id"))
    rating = relationship('ratingMaster', back_populates='packingF')

    packingMaterialId = Column(Integer, ForeignKey("packing.id"))
    packing_ = relationship('packing', back_populates='packingF')

    # packingTypeId = Column(Integer, ForeignKey("packingType.id"))
    # packingType_ = relationship('packingType', back_populates='packingT')

    # rel as parent
    actuatorCase = relationship('actuatorCaseData', cascade="all,delete", back_populates='packingF')

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = packingFriction.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


class packingTorque(db.Model):
    __tablename__ = "packingTorque"
    __mapper_args__ = {
        'polymorphic_identity': 'packingT',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    shaftDia = Column(Float)

    # rel as child
    ratingId = Column(Integer, ForeignKey("ratingMaster.id"))
    rating = relationship('ratingMaster', back_populates='torque')

    cvId = Column(Integer, ForeignKey("cvTable.id"))
    cv = relationship('cvTable', back_populates='torque')

    # rel as parent
    actuatorCase = relationship('actuatorCaseData', cascade="all,delete", back_populates='packingT')

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = packingTorque.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


class seatLoadForce(db.Model):
    __tablename__ = "seatLoadForce"
    __mapper_args__ = {
        'polymorphic_identity': 'seatLoad',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    seatBore = Column(Float)
    value = Column(Float)

    # rel as parent
    actuatorCase = relationship('actuatorCaseData', cascade="all,delete", back_populates='seatLoad')

    # rel as child
    trimTypeId = Column(Integer, ForeignKey("trimType.id"))
    trimType_ = relationship('trimType', back_populates='seatLoad')

    leakageClassId = Column(Integer, ForeignKey('seatLeakageClass.id'))
    leakage = relationship('seatLeakageClass', back_populates='seatLoad')

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = seatLoadForce.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


class seatingTorque(db.Model):
    __tablename__ = "seatingTorque"
    __mapper_args__ = {
        'polymorphic_identity': 'seatTorq',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    valveSize = Column(Float)
    discDia = Column(Float)
    discDia2 = Column(Float)
    cusc = Column(Float)
    cusp = Column(Float)
    softSeatA = Column(Float)
    softSeatB = Column(Float)
    metalSeatA = Column(Float)
    metalSeatB = Column(Float)

    

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = seatingTorque.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


class positioner(db.Model):
    __tablename__ = "positioner"
    __mapper_args__ = {
        'polymorphic_identity': 'pos',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    std = Column(String(200))
    manufacturer = Column(String(200))
    series = Column(String(200))
    moc = Column(String(200))
    enclosure = Column(String(200))
    spool_valve = Column(String(200))
    type = Column(String(200))
    technology = Column(String(200))
    communication = Column(String(200))
    action = Column(String(200))
    actions = Column(String(200))
    certificate = Column(String(200))
    model_no = Column(String(200))
    haz_class = Column(String(200))

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = positioner.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


class afr(db.Model):
    __tablename__ = "afr"
    __mapper_args__ = {
        'polymorphic_identity': 'afr_',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    manufacturer = Column(String(200))
    series = Column(String(200))
    moc = Column(String(200))
    size = Column(String(200))
    drain = Column(String(200))
    filter_size = Column(String(200))
    relive = Column(String(200))
    pressure_range = Column(String(200))
    fluid = Column(String(200))
    model = Column(String(200))
    remarks = Column(String(300))

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = afr.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()

class limitSwitch(db.Model):
    __tablename__ = "limitSwitch"
    __mapper_args__ = {
        'polymorphic_identity': 'limitS',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    make = Column(String(200))
    explosion = Column(String(200))
    moc = Column(String(200))
    sensor = Column(String(200))
    display = Column(String(200))
    model = Column(String(200))
    remark = Column(String(200))
    pressure_range = Column(String(200))

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = limitSwitch.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


class solenoid(db.Model):
    __tablename__ = "solenoid"
    __mapper_args__ = {
        'polymorphic_identity': 'solen',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    standard = Column(String(200))
    make = Column(String(200))
    series = Column(String(200))
    size = Column(String(200))
    type = Column(String(200))
    orifice = Column(String(200))
    cv = Column(String(200))
    model = Column(String(200))

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = solenoid.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


class cleaning(db.Model):
    __tablename__ = "cleaning"
    __mapper_args__ = {
        'polymorphic_identity': 'clean',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(100))

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = cleaning.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


class paintCerts(db.Model):
    __tablename__ = "paintCerts"
    __mapper_args__ = {
        'polymorphic_identity': 'paintC',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(100))

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = paintCerts.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


class paintFinish(db.Model):
    __tablename__ = "paintFinish"
    __mapper_args__ = {
        'polymorphic_identity': 'paintF',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(100))

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = paintFinish.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


class certification(db.Model):
    __tablename__ = "certification"
    
    __mapper_args__ = {
        'polymorphic_identity': 'cert',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(100))

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = certification.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


class positionerSignal(db.Model):
    __tablename__ = "positionerSignal"
    __mapper_args__ = {
        'polymorphic_identity': 'posSignal',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(100))

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = positionerSignal.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


class accessoriesData(db.Model):
    __tablename__ = "accessoriesData"
    __mapper_args__ = {
        'polymorphic_identity': 'accData',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)

    manufacturer = Column(String(200))
    model = Column(String(200))
    action = Column(String(200))
    afr = Column(String(200))
    transmitter = Column(String(200))
    limit = Column(String(200))
    proximity = Column(String(200))
    booster = Column(String(200))
    pilot_valve = Column(String(200))
    air_lock = Column(String(200))
    ip_make = Column(String(200))
    ip_model = Column(String(200))
    solenoid_make = Column(String(200))
    solenoid_model = Column(String(200))
    solenoid_action = Column(String(200))
    volume_tank = Column(String(200))
    ip_converter = Column(String(200))
    air_receiver = Column(String(200))
    tubing = Column(String(200))
    fittings = Column(String(200))
    cleaning = Column(String(200))
    certification = Column(String(200))
    paint_finish = Column(String(200))
    paint_cert = Column(String(200))
    sp1 = Column(String(200))
    sp2 = Column(String(200))
    sp3 = Column(String(200))
    rm = Column(String(200))
    hydro = Column(String(200))
    final = Column(String(200))
    paint_inspect = Column(String(200))
    packing_inspect = Column(String(200))
    vt1 = Column(String(200))
    vt2 = Column(String(200))

    # rel as child
    itemId = Column(Integer, ForeignKey("itemMaster.id"))
    item = relationship('itemMaster', back_populates='accessories')

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = accessoriesData.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


class valveArea(db.Model):
    __tablename__ = "valveArea"
    __mapper_args__ = {
        'polymorphic_identity': 'vArea',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    rating = Column(String(300))
    nominalPipeSize = Column(String(300))
    inMM = Column(String(300))
    inInch = Column(String(300))
    area = Column(String(300))

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = valveArea.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


class portArea(db.Model):
    __tablename__ = "portArea"
    __mapper_args__ = {
        'polymorphic_identity': 'pArea',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    model = Column(String(20))
    v_size = Column(String(20))
    seat_bore = Column(String(20))
    travel = Column(String(20))
    trim_type = Column(String(20))
    flow_char = Column(String(20))
    area = Column(String(20))

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = portArea.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


class hwThrust(db.Model):
    __tablename__ = "hwThrust"
    __mapper_args__ = {
        'polymorphic_identity': 'hw',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    failAction = Column(String(20))
    mount = Column(String(20))
    ac_size = Column(String(20))
    max_thrust = Column(String(20))
    dia = Column(String(20))

    @staticmethod
    def update(new_data, id):
        # note that this method is static and
        # you have to pass id of the object you want to update
        keys = new_data.keys()  # new_data in your case is filenames
        files = hwThrust.query.filter_by(id=id).first()  # files is the record
        # you want to update
        for key in keys:
            print(key)
            print(new_data[key])
            exec("files.{0} = new_data['{0}'][0]".format(key))
        db.session.commit()


class knValue(db.Model):
    __tablename__ = "knValue"
    __mapper_args__ = {
        'polymorphic_identity': 'kn',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    portDia = Column(Float)
    value = Column(Float)

    series = Column(String(20))

    # rel as child
    trimTypeId = Column(Integer, ForeignKey("trimType.id"))
    trimType_ = relationship('trimType', back_populates='kn')

    flowCharacId = Column(Integer, ForeignKey("flowCharacter.id"))
    flowCharacter_ = relationship('flowCharacter', back_populates='kn')

    flowDirId = Column(Integer, ForeignKey("flowDirection.id"))
    flowDirection_ = relationship('flowDirection', back_populates='kn')
    
    # seriesId = Column(Integer,Foreign)

class OTP(db.Model):
    __tablename__ = "OTP"
    __mapper_args__ = {
        'polymorphic_identity': 'otp',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    username = Column(String(100))
    otp = Column(BigInteger)
    time = Column(DateTime)


class kcTable(db.Model):
    __tablename__ = "kcTable"
    __mapper_args__ = {
        'polymorphic_identity': 'kcTable',
        'confirm_deleted_rows': False
    }
    id = Column(Integer, primary_key=True)
    valveStyle = Column(String(100))
    minSize = Column(Integer)
    maxSize = Column(Integer)
    trimType = Column(String(100))
    minDelP = Column(Integer)
    maxDelP = Column(Integer)
    formula = Column(Integer)