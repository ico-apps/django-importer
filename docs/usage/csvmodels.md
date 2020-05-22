# CsvModel

La pieza fundamental de esta aplicación es definir una clase que ayudará a la aplicación a entender el mapeo entre los modelos de django y el fichero csv.

Consiste en una clase que hereda de la clase CsvModel.

```
from djimporter import importers

class MyModelCsv(importers.CsvModel):
    pass
```

## Mapeo simple
Ahora vamos a definir el caso más simple de un mapeo entre un fichero csv y un model simple de django:

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

Entonces definiremos nuestra clase de csvmodel así:

```
from myModel import Person
from djimporter import importers

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

Ahora veremos la definición name de nuestra clase MyPersonCsv:
```
name = fields.CharField(match='first_name')
```
Esta linea nos hace un mapeo entre **name**, que es un nombre de columna que debe aparecer en el fichero csv, y **first_name** que es el campo del modelo al que vamos a asociar las datos de la columna.

Como se puede observar **last_name** aparece en fields pero no aparece definida en MyPersonCsv.
Esto indica que el nombre que debe aparecer en el fichero es igual que el que aparece definido en el modelo de django por lo que no vamos a necesitar una definición del mapeo. En cambio si vamos a necesitar indicarle a la clase MyPersonCsv que esta columna debe existir

