from datetime import datetime, timedelta
from peewee import *
from db_connection import db
from random import shuffle


class BaseModel(Model):
    created_at = DateTimeField(default=datetime.now())
    updated_at = DateTimeField(null=True)

    class Meta:
        database = db

    def save_model(self, data_model):
        self.save()


class Config(BaseModel):
    lush_url = CharField()
    lush_api_key = CharField()
    word_game_time_reveal = IntegerField(default=180)


class Webhook(BaseModel):
    webhook_id = AutoField(primary_key=True, help_text='Id do webhook')
    raw_data = TextField()


class Dare(BaseModel):
    dare_id = AutoField(primary_key=True, help_text='Id da Prenda')
    title = CharField(max_length=255)
    description = TextField(null=True)
    level = IntegerField()
    dare_type = IntegerField()
    value = IntegerField(null=True)
    action = IntegerField()
    '''
        dare_type:
            0 = like
            1 = gift
            2 = sub
        actions:
            0 = sem ação
            1 = Tempo Skin Pro
            2 = Lush   
    '''

    def get_action(self):
        if self.action == 1:
            pass
        if self.action == 2:
            pass

    @staticmethod
    def get_dare_type(dare_type, lush_on, last_dares):
        all_dares = {
            'light_dare': [],
            'medium_dare': [],
            'hard_dare': []
        }
        # last_ids = [d.dare_id for d in last_dares]
        dares = Dare.select().where(Dare.dare_type == dare_type)

        if not lush_on:
            dares = dares.where(Dare.action != 2)

        all_dares['light_dare'] = list(dares.where(Dare.level == 0))
        all_dares['medium_dare'] = list(dares.where(Dare.level == 1))
        all_dares['hard_dare'] = list(dares.where(Dare.level == 2))

        shuffle(all_dares['light_dare'])
        shuffle(all_dares['medium_dare'])
        shuffle(all_dares['hard_dare'])

        return all_dares


class WordModel(BaseModel):
    word = CharField()
    map_reveal = CharField()
    is_valid = BooleanField(default=True)

    @staticmethod
    def get_all_words():
        all_words = WordModel.select().where(WordModel.is_valid == True)
        if all_words:
            return list(all_words)
        return []


class ActionKey(BaseModel):
    action_key_id = AutoField(primary_key=True, help_text='Id do ActioKey')
    trigger_key = CharField(max_length=10)
    name = CharField(max_length=30)
    description = CharField(max_length=255)
    action_code = TextField()
    is_hot_key = BooleanField(default=False)
    is_active = BooleanField(default=False)
    is_valid = BooleanField(default=True)

    def execute_action(self, game):
        try:
            exec(self.action_code)
        except Exception as e:
            print(f'Erro ao Executar o Código {self.name}')


class LiveDay(BaseModel):
    live_day_id = AutoField(primary_key=True, help_text='Id do Seguidor')


class TikTokUser(BaseModel):
    tik_tok_id = AutoField(primary_key=True, help_text='Id do Seguidor')
    user_name = CharField()

    @staticmethod
    def get_user(tiktok_user):
        has_user = TikTokUser.select().where(TikTokUser.user_name == tiktok_user['user_id'])
        if has_user:
            return has_user.get()

        new_user = TikTokUser()
        new_user.user_name = tiktok_user['user_id']

        return new_user


class TikTokScore(BaseModel):
    live_day_id = ForeignKeyField(LiveDay, to_field='live_day_id', null=True)
    tik_tok_id = ForeignKeyField(TikTokUser, to_field='tik_tok_id', null=True)
    like_score = IntegerField()
    coin_score = IntegerField()


if __name__ == '__main__':
    db.create_tables([ActionKey])

    # dare_list = []
    #
    # raw_dare_list = [
    #     ('Mostra o Look', 'Mostra o Look', 0, 0, 0, 0),
    #     ('Mandar Beijinho', 'Mandar Beijinho', 0, 0, 0, 0),
    #     ('Mandar MiniCoração', 'Mandar MiniCoração', 0, 0, 0, 0),
    #     ('Desenha no Quadro', 'Desenha no Quadro', 0, 0, 0, 0),
    #     ('Fazer Careta', 'Fazer Careta', 0, 0, 0, 0),
    #     ('Imita Um Personagem', 'Imita Um Personagem', 0, 0, 0, 0),
    #     ('Desafina na Musica', 'Desafina na Musica', 0, 0, 0, 0),
    #     ('Fazer Pose', 'Fazer Pose', 0, 0, 0, 0),
    #     ('Finge Tocar Instrumento', 'Finge Tocar Instrumento', 0, 0, 0, 0),
    #     ('Rebola na Cadeira', 'Rebola na Cadeira', 1, 0, 0, 0),
    #     ('Dança na Cadeira', 'Dança na Cadeira', 1, 0, 0, 0),
    #     ('Desfilar na Passarela', 'Desfilar na Passarela', 1, 0, 0, 0),
    #     ('Mostra a Raba', 'Mostra a Raba', 1, 0, 0, 0),
    #     ('Fantasia de Professora', 'Fantasia de Professora', 1, 0, 0, 0),
    #     ('Faz Cara de Safada', 'Faz Cara de Safada', 1, 0, 0, 0),
    #     ('Pintada na Coxa', 'Pintada na Coxa', 1, 0, 0, 0),
    #     ('Ensina Professora', 'Ensina Professora', 1, 0, 0, 0),
    #     ('Conta Segredo', 'Conta Segredo', 1, 0, 0, 0),
    #     ('Ajeita a Flanelinha', 'Ajeita a Flanelinha', 2, 0, 0, 0),
    #     ('Carinho Por Cima', 'Carinho Por Cima', 2, 0, 0, 0),
    #     ('Carinho Por Dentro', 'Carinho Por Dentro', 2, 0, 0, 0),
    #     ('Carinho Em Volta', 'Carinho Em Volta', 2, 0, 0, 0),
    #     ('Contar um Segredo', 'Contar um Segredo', 2, 0, 0, 0),
    #     ('Dança na Camera', 'Dança na Camera', 2, 0, 0, 0),
    #     ('Mostra a Pintinha', 'Mostra a Pintinha', 2, 0, 0, 0),
    #     ('Carinho na Coxa', 'Carinho na Coxa', 2, 0, 0, 0),
    #     ('Mostra a Raba', 'Mostra a Raba', 0, 1, 0, 0),
    #     ('Fazer Pose', 'Fazer Pose', 0, 1, 0, 0),
    #     ('Rebola na Cadeira', 'Rebola na Cadeira', 0, 1, 0, 0),
    #     ('Faz Cara de Safada', 'Faz Cara de Safada', 0, 1, 0, 0),
    #     ('Carinho Por Cima', 'Carinho Por Cima', 0, 1, 0, 0),
    #     ('Pintada na Coxa', 'Pintada na Coxa', 0, 1, 0, 0),
    #     ('Rebola na Camera', 'Rebola na Camera', 1, 1, 0, 0),
    #     ('Mostra a Pintinha', 'Mostra a Pintinha', 1, 1, 0, 0),
    #     ('Ajeita a Flanelinha', 'Ajeita a Flanelinha', 1, 1, 0, 0),
    #     ('Dança na Camera', 'Dança na Camera', 1, 1, 0, 0),
    #     ('Carinho na Coxa', 'Carinho na Coxa', 1, 1, 0, 0),
    #     ('Carinho Por Dentro', 'Carinho Por Dentro', 2, 1, 0, 0),
    #     ('Molha o Dedinho', 'Molha o Dedinho', 2, 1, 0, 0),
    #     ('Agaixadinha na Camera', 'Agaixadinha na Camera', 2, 1, 0, 0),
    #     ('Carinho Em Volta', 'Carinho Em Volta', 2, 1, 0, 0),
    #     ('Vibra Fraco por 1 Seg', 'Vibra Fraco por 1 Seg', 0, 0, 1, 2),
    #     ('Vibra Fraco por 2 Seg', 'Vibra Fraco por 2 Seg', 0, 0, 2, 2),
    #     ('Vibra Fraco por 3 Seg', 'Vibra Fraco por 3 Seg', 1, 0, 3, 2),
    #     ('Vibra Medio por 1 Seg', 'Vibra Medio por 1 Seg', 1, 0, 1, 2),
    #     ('Vibra Medio por 2 Seg', 'Vibra Medio por 2 Seg', 2, 0, 2, 2),
    #     ('Vibra Medio por 3 Seg', 'Vibra Medio por 3 Seg', 2, 0, 3, 2),
    #     ('Vibra Medio por 2 Seg', 'Vibra Medio por 2 Seg', 0, 1, 2, 2),
    #     ('Vibra Medio por 3 Seg', 'Vibra Medio por 3 Seg', 0, 1, 3, 2),
    #     ('Vibra Fraco por 5 Seg', 'Vibra Fraco por 5 Seg', 1, 1, 5, 2),
    #     ('Vibra Medio por 4 Seg', 'Vibra Medio por 4 Seg', 1, 1, 4, 2),
    #     ('Vibra Medio por 5 Seg', 'Vibra Medio por 5 Seg', 1, 1, 5, 2),
    #     ('Vibra Forte por 2 Seg', 'Vibra Forte por 2 Seg', 2, 1, 2, 2),
    #     ('Vibra Forte por 3 Seg', 'Vibra Forte por 3 Seg', 2, 1, 3, 2),
    #     ('Vibra Forte por 5 Seg', 'Vibra Forte por 5 Seg', 2, 1, 5, 2)
    # ]
    #
    # for title, description, level, dare_type, value, action in raw_dare_list:
    #     dare_list.append(Dare(
    #         title=title,
    #         description=description,
    #         level=level,
    #         dare_type=dare_type,
    #         value=value,
    #         action=action
    #     ))
    #
    # with Dare._meta.database.atomic():
    #     Dare.bulk_create(dare_list)
