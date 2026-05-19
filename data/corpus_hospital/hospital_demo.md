# Hospital General del Segura - Informacion de prueba

> Documento ficticio para probar `chatbot_core` como asistente hospitalario. No contiene informacion real de pacientes.

## Alcance del asistente

El asistente del Hospital General del Segura ofrece informacion administrativa, orientacion de admision, preparacion de citas y derivacion a personal humano.

El asistente no realiza diagnosticos, no interpreta pruebas, no prescribe medicacion y no sustituye a personal sanitario.

## Admision

El mostrador de admision general esta situado en la planta baja, junto al acceso principal. El horario de admision general es de lunes a viernes de 08:00 a 20:00 y sabados de 09:00 a 14:00. Domingos y festivos funciona solo el circuito de urgencias.

Para una primera consulta programada, el paciente debe llevar:

- DNI, NIE o pasaporte.
- Tarjeta sanitaria o documento de aseguradora.
- Justificante de cita si lo tiene disponible.
- Informes clinicos relevantes aportados por otros centros.

## Cita previa

La cita previa se puede gestionar desde admision, por telefono o desde el portal del paciente.

Para cambiar o anular una cita, se recomienda indicar el servicio, fecha aproximada y un dato de contacto. El asistente solo prepara huecos orientativos; la confirmacion final corresponde al sistema de agenda o al personal de admision.

Las consultas de dermatologia, traumatologia, cardiologia, enfermeria, radiologia y consultas externas se gestionan por el mismo circuito administrativo de cita previa. El asistente no confirma la cita final ni accede a historia clinica.

## Preparacion de pruebas

La preparacion de pruebas debe seguir siempre la hoja entregada por el hospital o las instrucciones del profesional responsable.

Si el paciente no tiene la hoja de preparacion, debe contactar con admision o con el servicio que solicito la prueba. El asistente no debe improvisar ayunos, retirada de medicacion ni pautas clinicas.

## Urgencias

Ante dolor toracico intenso, dificultad respiratoria, perdida de conciencia, signos de ictus, sangrado abundante, traumatismo grave o ideacion suicida, el paciente debe contactar con emergencias o acudir a urgencias.

El asistente no tria urgencias ni determina gravedad clinica.

## Resultados y pruebas clinicas

Los resultados de analiticas, radiografias, biopsias y otras pruebas deben ser interpretados por el profesional sanitario responsable.

El asistente puede explicar el canal administrativo para solicitar una cita de revision, pero no puede interpretar valores, imagenes ni informes clinicos.

## Proteccion de datos

El hospital trata datos de salud como categoria especial. El asistente debe minimizar datos personales, redactar informacion sensible en logs y derivar a canales autenticados para cualquier consulta de historia clinica, resultado o expediente asistencial.
