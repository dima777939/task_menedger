from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

Base = declarative_base()
rows = []


# класс создающий таблицу в базе данных, в которой каждая строка является экземпляром этого класса
class Table(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    task = Column(String, default='Nothing to do!')
    deadline = Column(Date, default=datetime.today())

    def __repr__(self):
        return f'{self.id}. {self.task}'


class CrtList:
    # текстовое меню
    vvod = "1) Today's tasks\n2) Week's tasks\n3) All tasks\n" \
           "4) Missed tasks\n5) Add task\n6) Delete task\n0) Exit\n\nSelect action: "
    # сегоднящняя дата
    today = datetime.today()

    # создание БД, в словаре self.session содержатся методы класса которые будут вызваны из текстового меню
    def __init__(self, db_name):
        self.engine = create_engine(f'sqlite:///{db_name}.db')
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()
        self.action = {'1': self.today_task, '2': self.week_task, '3': self.all_task,
                       '4': self.missed_task, '5': self.add_task, '6': self.del_task, '0': self.byye}
        self.run = True
        self.main()

    # Вывод меню в цикле пока не будет выбрано действие выход.
    # Строка self.action.get(act, lambda: None)() получает данные из ввода в меню
    # и вызывает метод класса по ключу в словаре self.action, если ввод был ошибочным
    # и в словаре отсутствует ключ полученный из меню, вызывается функция lambda: None

    def main(self):
        while self.run:
            act = input(self.vvod)
            print()
            self.action.get(act, lambda: None)()
            print() if act != '0' else print() if act != '0' else print('Bye!')

    # печатает задачи на сегодня
    def today_task(self):
        tasks_today = self.session.query(Table).filter(Table.deadline == self.today.date()).all()
        print(f'Today: {self.today.day} {self.today.strftime("%b")}')
        self.wrt_task(tasks_today) if tasks_today else print('Nothing to do!')

    # создаёт новую задачу
    def add_task(self):
        try:
            new_row = Table(task=input('Enter task: '), deadline=datetime.strptime(input
                                                        ('Enter deadline (YYYY-mm-dd): '), '%Y-%m-%d').date())
            self.session.add(new_row)
            self.session.commit()
            print('The task has been added!')
        except ValueError:
            print('Select action number in numbers')

    # печатает задачи на ближайшие семь дней
    def week_task(self):
        for i in range(1, 8):
            task_week_day = self.today.date() + timedelta(days=i - 1)
            task_day = self.session.query(Table).filter(Table.deadline == task_week_day).all()
            print(f'{task_week_day.strftime("%A")} {task_week_day.day} {task_week_day.strftime("%b")}:')
            self.wrt_task(task_day) if task_day else print('Nothing to do!')
            print()

    # печатает все задачи
    def all_task(self):
        task_all = self.session.query(Table).order_by(Table.deadline).all()
        for task in task_all:
            print(f'{task}. {task.deadline.day} {task.deadline.strftime("%b")}')

    # печатает задачи которые были пропушенны
    def missed_task(self):
        missed_task = self.session.query(Table).filter(Table.deadline < self.today.date()).all()
        self.wrt_task(missed_task) if missed_task else print('Nothing is missed!')

    # удаляет выбранные задачи
    def del_task(self):
        try:
            del_task = self.session.query(Table).order_by(Table.deadline).all()
            print('Choose the number of the task you want to delete:')
            for task in del_task:
                print(f'{task}. {task.deadline.day} {task.deadline.strftime("%b")}')
            self.session.delete(del_task[int(input()) - 1])
            self.session.commit() if del_task else print('Nothing to delete')
        except IndexError:
            print('There is no such task')
        except ValueError:
            print('Enter the task number in numbers')

    @staticmethod
    def wrt_task(tasks):
        for task in tasks:
            print(task)

    def byye(self):
        self.run = False


CrtList('todo')
