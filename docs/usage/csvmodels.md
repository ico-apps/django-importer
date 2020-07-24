# CsvModel

La pieza fundamental de esta aplicación es definir una clase que ayudará a la aplicación a entender el mapeo entre los modelos de django y el fichero csv.

Consiste en una clase que hereda de la clase CsvModel.

```
from djimporter import importers

class MyModelCsv(importers.CsvModel):
    pass
```

## Mapeo simple
Llamamos un mapeo simple a aquellos mapeos que se construyen apartir de la relación entre un fichero csv y un modelo simple de django
Ahora vamos a definir este caso con un ejemplo

Supongamos que tenemos este modelo simple de django:

```
from django.db import models

class Person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
```

y lo queremos mapear con un fichero con este contenido:

```
last_name;name
Schmith;Susan
Wolf;Johan
```

Expondremos un ejemplo y luego definiremos cada una de sus partes.

Definimos una clase de csvmodel así:

```
from myModel import Person
from djimporter import importers, fields

class MyPersonCsv(importers.CsvModel):
    name = fields.CharField(match='first_name')

    class Meta:
        delimiter = ';'
        dbModel = Person
        fields = ['name', 'last_name']
```

Lo que primero vemos es una clase Meta en el interior de nuestra clase MyPersonCsv.
Esta clase Meta es la base para definir la relación entre los modelos de django y el fichero.
En ella vemos:
- **delimiter** que es una variable en la que definiremos que símbolo usaremos para delimitar las columnas de nuestro fichero csvmodel
- **dbModel** es el modelo de django al que vamos a asociar el fichero csv
- **fields** es la definición de las columnas que deben aparece en el fichero csv. El orden no es importante

Ahora veremos la definición **name** de nuestra clase MyPersonCsv:
```
name = fields.CharField(match='first_name')
```
Esta linea nos hace un mapeo entre **name**, que es un nombre de columna que debe aparecer en el fichero csv, y **first_name** que es el campo del modelo al que vamos a asociar las datos de la columna.

Como se puede observar **last_name** aparece en fields pero no aparece definida en MyPersonCsv.
Esto indica que el nombre que debe aparecer en el fichero es igual que el que aparece definido en el modelo de django por lo que no vamos a necesitar una definición del mapeo. En cambio si vamos a necesitar indicarle a la clase MyPersonCsv que esta columna debe existir

El siguiente punto que hay que resaltar es que no hemos definido nada para **last_name**, solo aparece en el listado fields. Si el nombre de la columna del csv y el del modelo coinciden no necesitamos definir nada más. Queremos advertir que si un campo del modelo no está definido en la variable **fields*+ entonces cogerá lo que aparezca en la variable **default** que hayamos descrito en nuestro modelo.


## Mapeo simple con una ForeingKey
Un mapeo simple con una ForeingKey exige que el objeto al que vamos a relacionar mediante la ForeingKey ya exista.
En muchos casos el ForeignKey es un valor que depende de cada instalación de una base de datos y suele ser diferente dependiendo en cada caso en particular.
Es por esta razón que no es aconsejable mapear el valor en sí del ForeinKey. Necesitamos encontrar el objeto por otros valores que lo hagan único, (como un slug o varios).
El ejemplo que proponemos para este caso es el siguiente:

Suponiendo que tenemos los siguientes modelos de django:

```
from django.db import models

class Musician(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    instrument = models.CharField(max_length=100)

class Album(models.Model):
    artist = models.ForeignKey(Musician, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    release_date = models.DateField()
    num_stars = models.IntegerField()
```

Nuestros datos de csv en un fichero son así:


```
first_name;surname;release_date;num_stars;name
Schmith;Susan;2000-01-01;5;aaa
Wolf;Johan;2001-01-01;4;bbb
```

En este caso definiremos nuestro csvmodel de esta manera:

```
class AlbumCsv(importers.CsvModel):
    first_name = fields.SlugRelatedField(match="artist", slug_field="musician__first_name")

    class Meta:
        delimiter = ';'
        dbModel = Album
        fields = ['name', 'release_date', 'num_stars', 'first_name']
```

Aquí vemos que el field **SlugRelatedField** nos consigue encontrar el objeto por medio del
parametro **slug_field**

## ForeingKey con más de una columna:
Hay unos casos donde necesitamos encontrar un objeto que será una ForeingKey de nuestro modelo Django
pero para hacerlo necesitamos más de un slug. Esto significa que debemos relacionar varias columnas
csv con un objeto. Para esto tenemos un Field que se llama **MultiSlugRelatedField**
Veamos un ejemplo:
Nuestros datos csv son los siguientes:

```
first_name;surname;release_date;num_stars;name
Susan;Schmith;2000-01-01;5;aaa
Wolf;Schmith;2001-01-01;4;bbb
```
En este csv tenemos que encontrar a un Artista desde las columnas first_name y surname.
Para ello usaremos una definición de CsvModel así:

```
class AlbumCsv(importers.CsvModel):
    artist = fields.MultiSlugRelatedField(
        matchs={"first_name": "musician__first_name", "surname": "musician__last_name"}
    )

    class Meta:
        delimiter = ';'
        dbModel = Album
        fields = ['name', 'release_date', 'num_stars']
        extra_fields = ['first_name', 'surname']
```
La variable **extra_fields** de la clase **Meta** nos permite definir nombres que deben aparecer en alguna de las columnas del csv que luego usaremos para encontrar al objeto **artist** pero no la usamos para un mapeo directo.


## pre_save y post_save.
Hay veces que necesitamos modificar los datos antes o despues de guardarlos.
Otras veces debemos ejecutar un proceso independiente del modelo si los datos tienen una caracteristica particular.
Para la mayoría de ejemplos complejos ***usaremos pre_save** o **post_save**.

En este caso definiremos nuestro ForeignKey usando un **pre_save** en csvmodel de esta manera:

```
class AlbumCsv(importers.CsvModel):

    class Meta:
        pre_save = ['get_musician']
        delimiter = ';'
        dbModel = Album
        fields = ['name', 'release_date', 'num_stars']
        extra_fields = ['first_name', 'surname']

        @classmethod
        def get_musician(cls, readrow):
            obj = readrow.object
            first_name = readrow.line['first_name']
            surname = readrow.line['surname']
            musician = Musician.objects.get(first_name=first_name, last_name=surname)
            obj.artist = musician
```

Como podemos observar no tenemos ningún field definido.
Como hemos indicado antes esto es así porque todos los fields del modelo tienen el mismo nombre que el de las columnas de nuestro fichero csv.

Lo siguiente que queremos resaltar es la definición de la variable **pre_save** que aparece en la subclase **Meta**.
**pre_save** es una lista de métodos de la clase Meta que se ejecutan antes de grabar el objeto en la base de datos. Esto nos permite definir un método donde capturar el objeto al que vamos a relacionar.
Como vemos, el objeto Album ya está creado cuando se ejecutan estas funciones **pre_save**. Nos aparece como **readrow.object**.

La variable de la calse **extra_fields** nos permite definir nombres que deben aparecer en alguna de las columnas del csv que luego usaremos en alguno de los métodos **pre_save** o **post_save**.
En este caso **first_name** y **surname** columnas de nuestro csv y las usaremos para poder capturar el objeto musician y así asociarlo a nuestro nuevo objeto en **obj.artist**.

## Un csv dos modelos
También podemos usar un pre_save o post_save para guardar desde un unico csv en dos modelos de django.
Hasta ahora hemos supuesto que el objeto artist estaba en la base de datos. Ahora vamos a suponer que no está y que nos lo trae el fichero csv.
Supongamos que tenemos el siguiente fichero csv:

```
first_name;surname;instrument;release_date;num_stars;name
Susan;Schmith;guitar;2000-01-01;5;aaa
Wolf;Schmith;violin;2001-01-01;4;bbb
```

Podríamos definir un CsvModel así:
```
class AlbumCsv(importers.CsvModel):

    class Meta:
        pre_save = ['set_musician']
        delimiter = ';'
        dbModel = Album
        fields = ['name', 'release_date', 'num_stars']
        extra_fields = ['first_name', 'surname']

        @classmethod
        def set_musician(cls, readrow):
            obj = readrow.object
            first_name = readrow.line['first_name']
            surname = readrow.line['surname']
            instrument = readrow.line['instrument']
            musician = Musician.objects.create(
                first_name=first_name, last_name=surname, instrument=instrument
            )
            obj.artist = musician
```
