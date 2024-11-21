from fastapi import APIRouter, Depends, status, HTTPException
# Сессия БД
from sqlalchemy.orm import Session
# Функция подключения к БД
from backend.db_depends import get_db
# Аннотации, Модели БД и Pydantic.
from typing import Annotated
from models import User, Task
from schemas import CreateTask, UpdateTask
# Функции работы с записями.
from sqlalchemy import insert, select, update, delete
# Функция создания slug-строки
from slugify import slugify

router = APIRouter(prefix='/task', tags=['task'])

'''Функция all_tasks ('/') - идентично all_users.'''
@router.get('/all_tasks') # или @router.get('/')?
async def all_tasks(db: Annotated[Session, Depends(get_db)]):
    tasks = db.scalars(select(Task)).all()
    #if tasks is None:
    if not tasks:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no tasks'
        )
    return tasks

'''Функция task_by_id ('/task_id') - идентично user_by_id.'''
@router.get('/task_id')
async def task_by_id(db: Annotated[Session, Depends(get_db)], task_id: str):
    task = db.scalars(select(Task).where(Task.id == task_id))
    #if task is None:
    if not task:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task was not found'
        )
    return task

'''Функция create_task ('/create'):
Дополнительно принимает модель CreateTask и user_id.
Подставляет в таблицу Task запись значениями указанными в CreateUser и user_id, если пользователь найден. 
Т.е. при создании записи Task вам необходимо связать её с конкретным пользователем User.
В конце возвращает словарь {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}
В случае отсутствия пользователя выбрасывает исключение с кодом 404 и описанием "User was not found"'''
@router.post('/create')
async def create_task(db: Annotated[Session, Depends(get_db)], createtask: CreateTask):
    #сперва проверяем user_id:
    check_user = db.scalar(select(User).where(User.id == createtask.user_id))
    #if check_user is None:
    if not check_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with id={createtask.user_id} for this task does not exist'
        )
    db.execute(insert(Task).values(title=createtask.title,
                                   priority=createtask.priority,
                                   completed=createtask.completed,
                                   user_id=createtask.user_id,
                                   slug=slugify(createtask.title)
                                   ))
    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }

'''Функция update_task ('/update') - идентично update_user.'''
@router.put('/update')
async def update_task(db: Annotated[Session, Depends(get_db)], task_id: int,
                      update_task_model: UpdateTask):
    task_update = db.scalar(select(Task).where(Task.id == task_id))
    #if task_update is None:
    if not task_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task was not found'
        )
    db.execute(update(Task).where(Task.id == task_id)
               .values(title=update_task_model.title,
                       priority=update_task_model.priority,
                       completed=update_task_model.completed,
                       user_id=update_task_model.user_id,
                       slug=slugify(update_task_model.title)
                       ))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Task update is successful!'
    }

'''Функция delete_task ('/delete') - идентично delete_user.'''
@router.delete('/delete')
async def delete_task(db: Annotated[Session, Depends(get_db)], task_id: int):
    task_delete = db.scalar(select(Task).where(Task.id == task_id))
    #if task_delete is None:
    if not task_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task was not found'
        )
    db.execute(delete(Task).where(Task.id == task_id))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Task was deleted successfully!'
    }