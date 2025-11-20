### 필요 명령어 

#### 사전 설정법

- 개별 설치 명령어 (pip install pandas)
- requirements.txt 전체 설치 (pip install -r .\requirements.txt)

#### 쿼리 작성법
query {    
  employees {  
    id  
    name  
    age  
    job  
    language  
    pay  
  }  
}  

#### 뮤테이션 작성법
mutation {
  createEmployee(
    input: {
      name: "Taylor"
      age: 29
      job: "backend"
      language: "python"
      pay: 410
    }
  ) {
    id
    name
    age
    job
    language
    pay
  }
}

mutation {
  updateEmployee(
    id: "2"
    input: {
      name: "Peter"
      age: 30
      job: "backend"
      language: "java"
      pay: 350
    }
  ) {
    id
    name
    age
    job
    language
    pay
  }
}

mutation {
  deleteEmployee(id: "3")
}