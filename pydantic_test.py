from pydantic_test import BaseModel, EmailStr, AnyUrl, Field, field_validator, model_validator, computed_field
from typing import List, Dict, Optional, Annotated

class Address(BaseModel):

    city: str
    state: str
    cep: str


class Patient(BaseModel):

    name: Annotated[str, Field(max_length=50, title='Name oof the patient',
                               description='Give the name of the patient in less than 50 chars',
                               examples=['Caio', 'Feliph'])]
    address: Address
    email: EmailStr
    linkedin_url: AnyUrl
    age: int 
    weight: Annotated[float, Field(gt=0, strict=True)]
    height: Annotated[float, Field(gt=1, strict=True)]
    married: Annotated[bool, Field(default=None, description='Is the patient married or not')]
    allergies: Annotated[Optional[List[str]], Field(default=None, max_length=5)]
    contact_details: Dict[str, str]

    @field_validator('email')
    @classmethod
    def email_validator(cls, value): 

        valid_domains = ['indt.org.br', 'icomp.ufam.edu.br']
        # teste@gmail.com
        domain_name = value.split('@')[-1]

        if domain_name not in valid_domains:
            raise ValueError('Not a valid domain')
        
        return value
    
    @field_validator('name', mode='after') # valida o dado bruto após a conversão de tipo
    @classmethod
    def tranform_name(cls, value):
        return value.upper()
    
    @field_validator('age') # valida o dado bruto depois da conversão de tipo
    @classmethod
    def validate_age(cls, value):
        if 0 < value < 120:
            return value
        else:
            raise ValueError('Age should be less than 120')
        
    @model_validator(mode='after') # valida objetos já construídos
    def validate_emergency_contact(self):
        if self.age > 60 and 'emergency' not in self.contact_details:
            raise ValueError('Patients older than 60 muste have an emergency contact')
        return self
    
    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/self.height**2)
        return bmi

def insert_patient_data(patient: Patient):

    print(patient.name)
    print(patient.age)
    print(patient.email)
    print(patient.linkedin_url)
    print(f'BMI {patient.bmi}')
    print(patient.address.city)
    print('inserted into database')

def update_patient_data(patient: Patient):

    print(patient.name)
    print(patient.age)
    print(patient.email)
    print(patient.linkedin_url)
    print('updated')

address_dict = {'city': 'Manaus', 'state':'Amazonas', 'cep':'69022200'}

address1 = Address(**address_dict)

patient_info = {'name':'caio', 'age':'22', 'email':'abc@indt.org.br','linkedin_url':'https://www.linkedin.com/in/caioantunes05/', 'weight':65.2, 'height':1.78, 'married':True, 
                'allergies': ['poeira', 'protetor solar'], 'contact_details':{'email':'citines@gmail.com', 'phone':'5592912345678'}, 'address': address1}

# pega cada chave do dicionário e transforma em argumento nomeado
patient1 = Patient(**patient_info)

insert_patient_data(patient1)

print(patient1.model_dump_json())
print('\n')
print(patient1.model_dump_json(include=['name']))
print(patient1.model_dump_json(exclude=['name']))
print(patient1.model_dump_json(exclude={'address':['state']}))