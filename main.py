from fastapi import FastAPI, Path, HTTPException, Query
import json
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
from fastapi.responses import JSONResponse


class Patient(BaseModel):
    # Modelo de dados que representa um paciente no sistema.
    # Campos obrigatórios com validações e descrições para documentação OpenAPI.
    id: Annotated[str, Field(..., description='ID do paciente',
                             examples=['P001'])]
    name: Annotated[str, Field(..., description='Nome do paciente')]
    city: Annotated[str, Field(..., description='Cidade onde o paciente mora')]
    age: Annotated[int, Field(..., gt=0, lt=130, description='Idade do paciente (anos)')]
    gender: Annotated[Literal['male', 'female', 'others'], Field(..., description='Gênero do paciente')]
    height: Annotated[float, Field(..., gt=0, description='Altura em metros')]
    weight: Annotated[float, Field(..., gt=0, description='Peso em quilogramas')]

    @computed_field
    @property
    def bmi(self) -> float:
        # Índice de massa corporal (IMC) calculado a partir de peso/altura.
        # Usamos round para simplificar a apresentação; mantém tipo numérico.
        return round(self.weight/self.height**2)

    @computed_field
    @property
    def verdict(self) -> str:
        # Classificação do IMC para fornecer um veredito simples.
        # Nota: os limites seguem uma convenção comum.
        if self.bmi < 18.5:
            return 'underweight'
        elif self.bmi < 30 and self.bmi >= 18.5:
            return 'normal'
        else:
            return 'obese'


class PatientUpdate(BaseModel):
    # Modelo usado para atualizações parciais de paciente.
    # Todos os campos são opcionais (default None) para permitir patches parciais.
    name: Annotated[Optional[str], Field(default=None, description='Nome do paciente')]
    city: Annotated[Optional[str], Field(default=None, description='Cidade onde o paciente mora')]
    age: Annotated[Optional[int], Field(default=None, gt=0, lt=130, description='Idade do paciente (anos)')]
    gender: Annotated[Optional[Literal['male', 'female', 'others']], Field(default=None, description='Gênero do paciente')]
    height: Annotated[Optional[float], Field(default=None, gt=0, description='Altura em metros')]
    weight: Annotated[Optional[float], Field(default=None, gt=0, description='Peso em quilogramas')]


app = FastAPI()  # instancia a aplicação FastAPI


def load_data():
    # Lê e retorna o conteúdo de `patients.json` como dicionário.
    # Lança exceção se o arquivo não existir; funções que chamam devem tratar.
    with open('patients.json', 'r') as f:
        data = json.load(f)
        return data


def save_data(data):
    # Serializa e salva o dicionário `data` em `patients.json`.
    with open('patients.json', 'w') as f:
        json.dump(data, f)


@app.get("/")
def hello():
    # Rota raiz: retorna uma mensagem simples de saudação/descrição da API.
    return {'message':'Patient Management System API'}


@app.get("/about")
def about():
    # Rota de informação: descreve brevemente a finalidade da API.
    return {'message':'A fully functional API to manage your patient records'}


@app.get("/view")
def view():
    # Retorna todo o banco de dados de pacientes (conteúdo do JSON)
    data = load_data()
    return data


@app.get('/patient/{patient_id}')
def view_patient(
    patient_id: str = Path(..., description='ID do paciente no banco', example='P001')
):
    # Recupera e retorna um paciente específico por `patient_id`.
    data = load_data()

    if patient_id in data:
        return data[patient_id]
    # Se não encontrado, retorna 404 com mensagem explicativa.
    raise HTTPException(status_code=404, detail='Patient not found')


@app.get('/sort')
def sort_patients(sort_by: str = Query(..., description='Sort on the basis of height, weight or BMI',),
                  order: str = Query('asc', description='Sort in ascending or desc order')):
    # Valida os campos aceitos para ordenação
    valid_fields = ['height', 'weight', 'bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f'Invalid field, select from {valid_fields}')

    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail='Invalid order, select between "asc" and "desc"')

    data = load_data()

    sort_order = True if order=='desc' else False

    # Ordena a lista de pacientes com base no campo `sort_by`.
    # Usa `get(..., 0)` para campos ausentes e `reverse` para ordem decrescente.
    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=sort_order)

    return sorted_data


@app.post('/create')
def create_patient(patient: Patient):

    # Carrega os dados existentes
    data = load_data()

    # Verifica se o paciente já existe para evitar duplicatas
    if patient.id in data:
        raise HTTPException(status_code=400, detail='Patient already exists')
    
    # Adiciona o novo paciente ao dicionário (exclui o campo id dos dados armazenados)
    data[patient.id] = patient.model_dump(exclude={'id'})
    
    # Persiste as alterações no arquivo JSON
    save_data(data)

    return JSONResponse(status_code=201, content={'message': 'patient added successfully'})


@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update: PatientUpdate):

    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    existing_patient = data[patient_id]

    # Converte o Pydantic model de atualização em um dict contendo apenas campos setados
    updated_patient = patient_update.model_dump(exclude_unset=True)

    # Atualiza os campos fornecidos no registro existente
    for key, value in updated_patient.items():
        existing_patient[key] = value
    
    # Para atualizar o IMC (campo calculado), recriamos um objeto Patient
    # adicionando o id temporariamente e gerando novamente os campos computados
    existing_patient['id'] = patient_id
    py_obj = Patient(**existing_patient)
    existing_patient = py_obj.model_dump(exclude={'id'})

    data[patient_id] = existing_patient

    save_data(data)

    return JSONResponse(status_code=200, content={'message': 'patient updated with success!'})


@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str):
    # Remove um paciente do banco (arquivo JSON) pelo seu ID
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=200, content={'message': 'Patient deleted with success'})
