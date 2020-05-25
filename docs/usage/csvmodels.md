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

El siguiente punto que hay que resaltar es que no hemos definido nada para **last_name*+, solo aparece en el listado fields. Si el nombre de la columna del csv y el del modelo coinciden no necesitamos definir nada más. Queremos advertir que si un campo del modelo no está definido en la variable **fields*+ entonces cogerá lo que aparezca en la variable **default** que hayamos descrito en nuestro modelo.


## Mapeo simple con una ForeingKey
Un mapeo simple con una ForeingKey exige que el objeto al que vamos a relacionar mediante la ForeingKey ya exista.
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

y el siguiente datos de csv en un fichero:


```
first_name;surname;name;release_date;num_stars;
Schmith;Susan;2000-01-01;5;aaa
Wolf;Johan;2001-01-01;4;bbb
```

En este caso definiremos nuestro csvmodel de esta manera:

```
class AlbumCsv(importers.CsvModel):

    class Meta:
        pre_save = ['get_taxonomy']
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

Como podemos observar no tenemos ningún field definido. Esto es así porque todos los fields del modelo tienen el mismo nombre que el de las columnas de nuestro fichero csv.

Lo siguiente que queremos resaltar es la definición de la variable **pre_save** que aparece en la subclase **Meta**.
**pre_save** es una lista de métodos de la clase Meta que se ejecutan antes de grabar el objeto en la base de datos. Esto nos permite definir un método donde capturar el objeto al que vamos a relacionar.
Como vemos, el objeto Album ya está creado cuando se ejecutan estas funciones **pre_save**. Nos aparece como **readrow.object**.

La variable de la calse **extra_fields** nos permite definir nombres que deben aparecer en alguna de las columnas del csv que luego usaremos en alguno de los métodos **pre_save** o **post_save**.
En este caso **first_name** y **surname** columnas de nuestro csv y las usaremos para poder capturar el objeto musician y así asociarlo a nuestro nuevo objeto en **obj.artist**.
