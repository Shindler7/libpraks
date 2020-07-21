"""
Конфигурационные модели для SQL.
"""
import logging
from datetime import datetime

from flask_login import UserMixin
from requests import get
from sqlalchemy import event, UniqueConstraint
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app import application, db_lib
from app import login_manager


subscribes_table = db_lib.Table(
    'Subscribes', db_lib.metadata,
    db_lib.Column('user_id', db_lib.Integer,
                  db_lib.ForeignKey('User.id')
                  ),
    db_lib.Column('content_id', db_lib.Integer,
                  db_lib.ForeignKey('Content.id')
                  ),
    UniqueConstraint('user_id', 'content_id')
)


class UserManager:

    def create(self, *, nick: str, passd: str):
        """
        Создаёт нового пользователя. Возвращает объект пользователя.
        """

        user = User(nickname=nick)
        user.set_password(passd)
        db_lib.session.add(user)
        db_lib.session.commit()

        return user

    def get(self, *, nick: str, passd: str):
        """
        Возвращает объект пользователя (user) после проведения проверок.
        В случае любого нарушения возвращает None.
        """

        user = User.query.filter_by(nickname=nick).first()
        if user is None:
            return None
        if not user.check_password(passd):
            return None
        if not user.active:
            return None

        return user


    def get_or_create(self, *, nickname: str, social_id: str):
        """
        Создает объект пользователя (user) или возвращает его, если он уже
        существует.
        """

        user = User.query.filter_by(nickname=nickname, social_id=social_id).first()
        if user is None:
            user = User(nickname=nickname, social_id=social_id)
            db_lib.session.add(user)
            db_lib.session.commit()

        return user


    def invert_arg(self, id_num: int, *args):
        """
        Оборачивает аргументы пользователя isadmin и active.
        Автоматически меняет для указанного аргумента True на False и наоборот.
        """
        user = User.query.get(id_num)

        if 'isadmin' in args:
            user.isadmin = not user.isadmin

        if 'active' in args:
            user.active = not user.active

        db_lib.session.commit()

    def remove(self, id_num: int):
        """
        Удаление пользователя по ID.
        """

        User.query.filter(User.id == id_num).delete()
        db_lib.session.commit()


class CategoryManager:

    def add(self, *, name: str, f_name: str = None):
        """
        Добавляет категорию.
        """
        name = name.strip().lower()
        if f_name:
            f_name = f_name.strip().lower()

        category = Category()
        category.name = name
        category.fname = f_name

        db_lib.session.add(category)
        db_lib.session.commit()

    def edit(self, id_num: int, *, name: str, f_name: str):
        """
        Редактирование существующей записи категории.
        """

        category = Category.query.get(id_num)
        category.name = name.strip().lower()
        if f_name:
            category.fname = f_name.strip().lower()
        db_lib.session.add(category)
        db_lib.session.commit()

    def get_all(self, *, sort: bool = True):
        """
        Возвращает все категории.
        """

        query = Category.query
        if sort:
            query = query.order_by(Category.name)
        return query.all()

    def remove(self, id_num: int):
        """
        Удаляет выбранный элемент по ID.
        """

        Category.query.filter(Category.id == id_num).delete()
        db_lib.session.commit()


class TypesManager:

    def add(self, *, name: str, f_name: str = None):
        """
        Добавляет новый тип данных.
        """
        name = name.strip().lower()
        if f_name:
            f_name = f_name.strip().lower()

        types = Types()
        types.name = name
        types.fname = f_name

        db_lib.session.add(types)
        db_lib.session.commit()

    def edit(self, id_num: int, name: str, f_name: str):
        """
        Редактирование существующей записи типа материалов.
        """

        types = Types.query.get(id_num)
        types.name = name.strip().lower()
        if f_name:
            types.fname = f_name.strip().lower()

        db_lib.session.add(types)
        db_lib.session.commit()

    def get_all(self, *, sort: bool = True):
        """
        Возвращает все типы.
        """

        query = Types.query
        if sort:
            query = query.order_by(Types.name)
        return query.all()

    def get_by(self, category: str, *,
               dictionary: bool = False,
               sort: bool = True):
        """
        Формирует выборку типов, связанных с переданной категорией.
        """

        if not category:
            query = self.get_all(sort=sort)
            if dictionary:
                return {type_.id: type_.name for type_ in query}
            return query

        cats = Category.query.filter(Category.name == category).first()
        type_ids = db_lib.session.query(Content.types_id).filter(
            Content.category_id == cats.id).distinct()

        query = Types.query.filter(Types.id.in_(type_ids))
        if sort:
            query = query.order_by(Types.name)

        query = query.all()

        if dictionary:
            return {type_.id: type_.name for type_ in query}

        return query

    def remove(self, id_num: int):
        """
        Удаляет выбранный элемент по ID.
        """

        Types.query.filter(Types.id == id_num).delete()
        db_lib.session.commit()


class ContentManager:

    def add(self, **data):
        """
        Добавляет новую запись в таблицу Content.
        Необходимые параметры:
        name, url, lang, types_id, category_id
        """

        content = Content(**data)
        db_lib.session.add(content)
        db_lib.session.commit()

    def get_all(self, *, sort: bool = True):
        """
        Возвращает всю таблицу Content.
        """

        query = Content.query
        if sort:
            query = query.order_by(Content.types_id, Content.name)
        return query.all()

    def get_by(self, *, category: str, types: str, sort: bool = True):
        """
        Формирует выборку на основании переданной категории и (или) типа.
        """

        if category:
            query = Category.query.filter(Category.name == category).first()
            query = query.content
        else:
            query = Content.query

        if types:
            ts = Types.query.filter(Types.name == types).first()
            query = query.filter(Content.types_id == ts.id)

        if sort:
            query = query.order_by(Content.types_id, Content.name)

        return query.all()

    def get_all_lang(self):
        """
        Возвращает список уникальных значений lang в таблице Content.
        """

        return db_lib.session.query(Content.lang).distinct().all()

    def remove(self, id_num: int):
        """
        Удаление записи по ID.
        """

        Content.query.filter(Content.id == id_num).delete()
        db_lib.session.commit()


class User(UserMixin, db_lib.Model):
    """
    Таблица User - информация о зарегистрированных пользователях.
    """

    __tablename__ = 'User'

    id = db_lib.Column(db_lib.Integer, primary_key=True)
    social_id = db_lib.Column(db_lib.String(64), nullable=True, unique=True)
    nickname = db_lib.Column(db_lib.String(64), nullable=False, unique=True)
    password_hash = db_lib.Column(db_lib.String(128), nullable=True)
    isadmin = db_lib.Column(db_lib.Boolean, default=False)
    active = db_lib.Column(db_lib.Boolean, default=True)

    content_id = relationship('Content', secondary=subscribes_table,
                              lazy='dynamic', backref='users')

    manager = UserManager()

    def set_password(self, password: str) -> None:
        """
        Создание хеш-слепка пароля.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """
        Проверка соответствия хэш-слепка пароля введённому паролю.
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User: nickname={self.nickname}, isadmin={self.isadmin}>'

    def __str__(self):
        return self.nickname


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class Category(db_lib.Model):
    """
    Таблица Category - содержательная характеристика (python, sql и т.п.).
    Один ко многим.
    """

    __tablename__ = 'Category'

    id = db_lib.Column(db_lib.Integer, primary_key=True)
    name = db_lib.Column(db_lib.String(100), nullable=False, unique=True)
    fname = db_lib.Column(db_lib.String(100), nullable=True, unique=True)

    content = relationship('Content', backref='Category', lazy='dynamic')

    manager = CategoryManager()

    def __repr__(self):
        return f'<Types(id="{self.id}", name="{self.name}")>'

    def __str__(self):
        return self.name


class Types(db_lib.Model):
    """
    Таблица Types - тип источника (сайт, видео, игра и т.д.).
    Один ко многим.
    """

    __tablename__ = 'Types'

    id = db_lib.Column(db_lib.Integer, primary_key=True)
    name = db_lib.Column(db_lib.String(200), nullable=False, unique=True)
    fname = db_lib.Column(db_lib.String(100), nullable=True, unique=True)

    content = relationship('Content', backref='Types', lazy='dynamic')

    manager = TypesManager()

    def __repr__(self):
        return f'<Types(id="{self.id}", name="{self.name}")>'

    def __str__(self):
        return self.name


class Content(db_lib.Model):
    """
    Таблица Content - основные сведения об источнике.
    """

    __tablename__ = 'Content'

    id = db_lib.Column(db_lib.Integer, primary_key=True)
    name = db_lib.Column(db_lib.String(200), nullable=False)
    url = db_lib.Column(db_lib.String(300), nullable=False, unique=True)
    date = db_lib.Column(db_lib.DateTime, nullable=False, default=datetime.now)
    lang = db_lib.Column(db_lib.String(10), nullable=False)
    img_url = db_lib.Column(db_lib.String(200), nullable=True)

    category_id = db_lib.Column(db_lib.Integer(),
                                db_lib.ForeignKey('Category.id'))
    types_id = db_lib.Column(db_lib.Integer(), db_lib.ForeignKey('Types.id'))

    user_id = relationship('User', secondary=subscribes_table,
                           lazy='dynamic', backref='contents')

    manager = ContentManager()

    def __repr__(self):
        return f'<Content(name="{self.name}", url="{self.url}",' \
               f' date="{self.date}", lang="{self.lang}")>'

    def __str__(self):
        return self.name


@event.listens_for(Content, 'after_insert')
def receive_after_insert(mapper, connection, target):
    """
    Обработка новой записи в Content после внесения в БД.
    Вызов "в тени" метода создания скриншота ссылки.
    """
    params = {
        'id': target.id,
        'url': target.url,
        'token': application.config['SCREEN_SERVER_SECRET_KEY'],
        'host': application.config['PROJECT_HOST']
    }
    url = application.config['SCREEN_SERVER']
    r = get(url, params=params)
    logging.info(msg=f'Запрос отправлен. Статус ответа: {r.status_code}')
