import discord, json, datetime
import mysql.connector
from discord.ext import commands
from discord import Intents

intents = Intents.all()
intents.typing = False
intents.members = True
client = discord.Client(intents=intents)


def connect_db():
    host = "b2jvfbwwzwgru1w4egfx-mysql.services.clever-cloud.com"
    database = "b2jvfbwwzwgru1w4egfx"
    user = "umpbhpsayjpkxxrn"
    password = "MPQecUPZwyGfZ922o8wV"
    port = 3306
    try:
        connection = mysql.connector.connect(
            host=host, database=database, user=user, password=password, port=port
        )
    except mysql.connector.Error as err:
        print(f"Error de conexión: {err}")
    else:
        print("Conectado a la base de datos MySQL")
        return connection


def disconnect_db(connection):
    # cursor.close()

    # Cerrar conexión
    connection.close()


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    name = "Usuarios"

    db = connect_db()
    #  drop_all_tables(db)
    # disconnect_db(db)
    cursor = db.cursor()
    try:
        select_sql = f"SELECT * FROM {name};"
        cursor.execute(select_sql)
        rows = cursor.fetchall()
        for row in rows:
            print(row)
        disconnect_db(db)
    except Exception as e:
        print(f"La tabla {name} no existe")


@client.event
async def on_guild_join(guild):
    print(f"Nuevo servidor conectado {guild.name}")
    # print(servidor)
    #  for message in guild.channels
    # print(guild.channels)
    await collector(guild)


async def collector(guild):
    servidor_name = guild.name
    servidor_id = guild.id
    members = await get_members(guild)
    canales = await get_channels(guild, True)
    mensajes = await get_channels(guild, False)
    create_db()
    print(f"se ha unido al servidor {servidor_name}")
    db = connect_db()
    cursor_servidor = db.cursor()
    cursor_members = db.cursor()
    cursor_mensajes = db.cursor()
    # drop_table_sql = f"DROP TABLE IF EXISTS Servidores;"
    # cursor_servidor.execute(drop_table_sql)
    valores_servidor = (servidor_id, servidor_name, canales)
    insert_servidor = "INSERT INTO Servidores (id_servidor, nombre_servidor,canales) VALUES (%s, %s,%s)"
    insert_mensajes = "INSERT INTO Mensajes (id_servidor, nombre_canal, id_canal, nombre_usuario, id_usuario, fecha, contenido) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    insert_usuarios = "INSERT INTO Usuarios (nombre_usuario, id_usuario, fecha_ingreso, id_servidor) VALUES (%s, %s, %s, %s)"
    try:
        cursor_servidor.execute(insert_servidor, valores_servidor)
        db.commit()
        for member in members:
            # print(member)
            cursor_members.execute(insert_usuarios, member)
            db.commit()
        for data in mensajes:
            cursor_mensajes.execute(
                "SELECT id_usuario FROM Usuarios WHERE id_usuario = %s", (data[4],)
            )
            result = cursor_mensajes.fetchone()
            #  cursor_mensajes.execute(insert_mensajes, data)
            #
            if result:
                # El id_usuario existe, procede con la inserción
                print("entramos")
                cursor_mensajes.execute(insert_mensajes, data)
            else:
                # print(data)
                # print(f"data 4 {data[4]} y data5{data[5]}")
                fail = (data[3], data[4], None, data[0])
                cursor_members.execute(insert_usuarios, fail)
                db.commit()
                print(f"El id_usuario {data[4]} no existe en la tabla Usuarios.")
        db.commit()
        disconnect_db(db)
    except Exception as e:
        print(f"Error {e}")


async def get_channels(guild, bool):
    canales = await guild.fetch_channels()
    lista = []
    if bool:
        json_canales = {}
        for canal in canales:
            if isinstance(canal, discord.TextChannel):
                json_canales[canal.id] = {
                    "nombre_canal": canal.name,
                    "tipo_canal": "texto",
                }
            elif isinstance(canal, discord.VoiceChannel):
                json_canales[canal.id] = {
                    "nombre_canal": canal.name,
                    "tipo_canal": "voz",
                }
        return json.dumps(json_canales)
    else:
        for canal in canales:
            if isinstance(canal, discord.TextChannel):
                # mensajes = await canal.history(limit=None)
                # (id_servidor, nombre_canal,id_canal, nombre_autor, id_autor, fecha, contenido)
                async for mensaje in canal.history(limit=None):
                    if not mensaje.author.bot:
                        id_servidor = guild.id
                        nombre_canal = canal.name
                        id_canal = canal.id
                        nombre_usuario = mensaje.author.name
                        id_usuario = mensaje.author.id
                        fecha = mensaje.created_at.isoformat()
                        contenido = mensaje.clean_content
                        lista.append(
                            (
                                id_servidor,
                                nombre_canal,
                                id_canal,
                                nombre_usuario,
                                id_usuario,
                                fecha,
                                contenido,
                            )
                        )

            elif isinstance(canal, discord.VoiceChannel):
                async for mensaje in canal.history(limit=None):
                    if not mensaje.author.bot:
                        id_servidor = guild.id
                        nombre_canal = canal.name
                        id_canal = canal.id
                        nombre_usuario = mensaje.author.name
                        id_usuario = mensaje.author.id
                        fecha = mensaje.created_at.isoformat()
                        contenido = mensaje.clean_content
                        lista.append(
                            (
                                id_servidor,
                                nombre_canal,
                                id_canal,
                                nombre_usuario,
                                id_usuario,
                                fecha,
                                contenido,
                            )
                        )
        return reversed(lista)


async def add_user(member):
    db = connect_db()
    cursor_members = db.cursor()
    insert_usuarios = "INSERT INTO Usuarios (nombre_usuario, id_usuario, fecha_ingreso, id_servidor) VALUES (%s, %s, %s, %s)"
    data = (
        member.name,
        member.id,
        member.joined_at.isoformat(),
        member.guild.id,
    )
    cursor_members.execute(insert_usuarios, data)
    db.commit()
    disconnect_db(db)


async def get_members(guild):
    members = guild.fetch_members()
    list_member = []
    async for member in members:
        list_member.append(
            (member.name, member.id, member.joined_at.isoformat(), guild.id)
        )

    return list_member


def create_db():
    db = connect_db()
    cursor = db.cursor()

    crear_tabla_servidores = """
    CREATE TABLE IF NOT EXISTS Servidores (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre_servidor VARCHAR(255) NOT NULL,
        id_servidor BIGINT NOT NULL UNIQUE,
        canales JSON
    );
    """
    cursor.execute(crear_tabla_servidores)

    crear_tabla_usuarios = """
CREATE TABLE IF NOT EXISTS Usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario VARCHAR(255) NOT NULL,
    id_usuario BIGINT NOT NULL,
    fecha_ingreso DATE,
    id_servidor BIGINT NOT NULL,
    UNIQUE (nombre_usuario, id_servidor), 
    INDEX (id_usuario),
    FOREIGN KEY (id_servidor) REFERENCES Servidores(id_servidor)
);
"""

    cursor.execute(crear_tabla_usuarios)

    crear_tabla_mensajes = """
    CREATE TABLE IF NOT EXISTS Mensajes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_servidor BIGINT NOT NULL,
        nombre_canal VARCHAR(255) NOT NULL,
        id_canal BIGINT NOT NULL,
        nombre_usuario VARCHAR(255) NOT NULL,
        id_usuario BIGINT NOT NULL,
        fecha DATETIME NOT NULL,
        contenido TEXT NOT NULL,
        FOREIGN KEY (id_servidor) REFERENCES Servidores(id_servidor),
        FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario)
    );
    """
    cursor.execute(crear_tabla_mensajes)

    # Guardar cambios y cerrar la conexión
    db.commit()
    disconnect_db(db)


def drop_all_tables(connection):
    cursor = connection.cursor()

    # Desactivar verificación de claves foráneas temporalmente
    cursor.execute("SET foreign_key_checks = 0;")

    # Lista de nombres de tablas
    tables = ["Servidores", "Usuarios", "Mensajes"]

    for table in tables:
        drop_table_sql = f"DROP TABLE IF EXISTS {table};"
        cursor.execute(drop_table_sql)

    # Reactivar verificación de claves foráneas
    cursor.execute("SET foreign_key_checks = 1;")

    connection.commit()
    cursor.close()


@client.event
async def on_message(message):
    channel = message.channel
    fetch = await channel.fetch_message(message.id)
    if not message.author.bot:
        db = connect_db()
        cursor = db.cursor()
        insert = "INSERT INTO Mensajes (id_servidor, nombre_canal, id_canal, nombre_usuario, id_usuario, fecha, contenido) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        id_servidor = message.guild.id
        nombre_canal = message.channel.name
        id_canal = message.channel.id
        nombre_usuario = message.author.name
        id_usuario = message.author.id
        fecha = message.created_at.isoformat()
        contenido = message.clean_content
        data = (
            id_servidor,
            nombre_canal,
            id_canal,
            nombre_usuario,
            id_usuario,
            fecha,
            contenido,
        )
        cursor.execute(insert, data)
        db.commit()
        disconnect_db(db)
    if fetch.content == "ef":
        # print(fetch.content)
        # mem = message.guild.fetch_members()
        print("mem")
    #   print(id)
    # print(fetch.created_at)
    # print(message.author)


@client.event
async def on_member_remove(member):
    print(f"{member.name} ha sido expulsado del servidor.")
    # Puedes realizar otras acciones aquí, como enviar un mensaje, almacenar información, etc.


@client.event
async def on_member_join(member):
    print(f"{member.name} se ha unido al servidor el {member.joined_at}")
    await add_user(member)
    # Puedes realizar otras acciones aquí, como enviar un mensaje de bienvenida, asignar roles, etc.


@commands.command(name="members")
async def members_command(self, ctx):
    members = await ctx.guild.fetch_members()

    for member in members:
        await ctx.send(member.name)

    # help(discord.Message)


client.run("MTIwMDE0OTM2NjIwNDI4MDkxMg.GHEL3Z._7BaqMwqz3AGCOfoNSWzdSWQRTvQCs9gFM10SM")
