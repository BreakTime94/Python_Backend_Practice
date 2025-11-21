import strawberry, redis
from typing import Optional, List
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from db.database import Base,Session as SessionLocal, engine
from db.models import EmployeeModel

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

r= redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

EMPLOYEE_ID_COUNTER_KEY = "employee:id:counter"
EMPLOYEE_ALL_SET_KEY = "employee:all-set"

def employee_redis_key(emp_id: int) -> str:
  return f"employee:id:{emp_id}"

@strawberry.type
class Employee:
  id: int
  name: str
  age: int
  job: str
  language: str
  pay: int

@strawberry.input
class EmployeeInput:
  name: str
  age: int
  job: str
  language: str
  pay: int

# ORM 객체 -> GRAPHQL 타입 변환 도우미
def redis_to_grpahql(emp_id: int, data: dict) -> Employee:
  return Employee(
    id = emp_id,
    name = data.name,
    age= data.age,
    job= data.job,
    language= data.language,
    pay= data.pay
  )

@strawberry.type
class Query:
  @strawberry.field
  def employees(self) -> List[Employee]:
    ids = r.smembers(EMPLOYEE_ALL_SET_KEY)
    result: List[Employee] = []
    for id_str in ids:
      key = employee_redis_key(int(id_str))
      data = r.hgetall(key)
      if data:
        result.append(redis_to_grpahql(int(id_str), data))

    result.sort(key=lambda emp: emp.id)
    return result
    # with SessionLocal() as db:
    #   rows = db.query(EmployeeModel).all()
    #   return [orm_to_grpahql(row) for row in rows]
    # return EMPLOYEES

  # @strawberry.field
  # def employee(self, id: strawberry.ID) -> Employee:
  #
  #   for emp in EMPLOYEES:
  #     if emp.id == id:
  #       return emp

@strawberry.type
class Mutation:
  @strawberry.mutation
  def createEmployee(self, input: EmployeeInput) -> Employee:

    with SessionLocal() as db:
      new_emp = EmployeeModel(
        name = input.name,
        age = input.age,
        job = input.job,
        language = input.language,
        pay = input.pay
      )
      db.add(new_emp)
      db.commit()
      db.refresh(new_emp)

      return orm_to_grpahql(new_emp)

    # new_id = max([e.id for e in EMPLOYEES]) + 1
    #
    # 등록쿼리
    # new_emp = Employee(
    #   id = new_id,
    #   name = input.name,
    #   age = input.age,
    #   job = input.job,
    #   language = input.language,
    #   pay = input.pay
    # )
    #
    # EMPLOYEES.append(new_emp)
    # return new_emp

  @strawberry.mutation
  def updateEmployee(self, id: int, input: EmployeeInput) -> Employee:
    emp_id = id
    with SessionLocal() as db:
      row = db.query(EmployeeModel).filter(EmployeeModel.id == emp_id).first()
      if row is None:
        raise ValueError(f"Employee with id {emp_id} not found")

      row.name = input.name,
      row.age = input.age,
      row.job = input.job,
      row.language = input.language,
      row.pay = input.pay

      db.commit()
      db.refresh(row)

      return orm_to_grpahql(row)

    # # 수정쿼리
    # for idx, emp in enumerate(EMPLOYEES):
    #   if emp.id == id:
    #     update = Employee(
    #       name = input.name,
    #       age = input.age,
    #       job = input.job,
    #       language = input.language,
    #       pay = input.pay
    #     )
    #     EMPLOYEES[idx] = update
    #     return update
    #
    # raise ValueError("Employee not found")

  @strawberry.mutation
  def deleteEmployee(self, id: int) -> int:

    with SessionLocal() as db:
      row = db.query(EmployeeModel).filter(EmployeeModel.id == id).first()
      if row is None:
        raise ValueError(f"Employee with id {id} not found")

      db.delete(row)
      db.commit()
      db.refresh(id)
      return id

    # #삭제쿼리
    # global EMPLOYEES
    # EMPLOYEES = [e for e in EMPLOYEES if e.id != id]
    # return id

schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)


def init_sample_data():
  """서버 최초 실행 시 샘플 직원 데이터 넣기 (이미 있으면 스킵)"""
  from sqlalchemy.exc import IntegrityError

  with SessionLocal() as db:
    # 이미 데이터가 있으면 초기화 X
    if db.query(EmployeeModel).count() > 0:
      return

    samples = [
      EmployeeModel(name="John", age=35, job="frontend", language="react", pay=400),
      EmployeeModel(name="Peter", age=28, job="backend", language="java", pay=300),
      EmployeeModel(name="Sue", age=38, job="publisher", language="javascript", pay=400),
      EmployeeModel(name="Susan", age=45, job="pm", language="python", pay=500),
    ]

    db.add_all(samples)
    db.commit()

app= FastAPI()

@app.on_event("startup")
def startup_event():
  Base.metadata.create_all(bind=engine)
  init_sample_data()


# CORS 설정
origins = [
  "http://localhost:3000",
  "http://127.0.0.1:3000",
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
async def root():
  return {"message": "FastAPI GraphQL Employee 서버 동작 중"}

