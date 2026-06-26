# Guion de narración para grabar — MaduraApp Eval 3

> Lee esto en voz alta mientras grabas, una sección por slide. Ritmo natural ≈ 14 minutos. Respira en los puntos.

## Slide 1 — Portada

Hola, buenos días. Mi nombre es Claudio Aro y voy a presentar la defensa del Estado de Avance 3 de mi proyecto: MaduraApp, un sistema de análisis de madurez de frutas mediante visión computacional. En los próximos quince minutos les voy a mostrar el plan de pruebas que diseñé, cómo lo apliqué a los componentes del sistema, y las mejoras que hice a partir de esos resultados. Comencemos.

## Slide 2 — Agenda

Esta es la ruta que voy a seguir. Primero el contexto del proyecto para situar el problema. Luego entro al corazón de esta evaluación: el plan de pruebas, su aplicación y los resultados. Después, las mejoras que apliqué al producto. Y cierro con la conclusión y el trabajo que queda pendiente.

## Slide 3 — Contexto del proyecto

Partamos por el problema. En Chile se pierde entre el veinte y el cuarenta por ciento de la fruta después de la cosecha, según la FAO y ODEPA. Una de las causas raíz es que no existe una forma objetiva y accesible de saber cuándo una fruta está en su punto óptimo de consumo: la gente se guía por el ojo o el tacto, y se equivoca. MaduraApp resuelve esto con una foto. El usuario elige la fruta, toma una foto, y la aplicación le dice el estado de madurez (inmaduro, óptimo o sobremaduro) con un semáforo de colores y una recomendación. Funciona con cuatro frutas: aguacate, plátano, tomate y mango. Por debajo, la app está hecha en Android nativo con Kotlin, el servidor es una API en FastAPI, y el modelo de inteligencia artificial es YOLO veintiséis, que entrené y que alcanza una precisión, medida en mAP cincuenta, de cero coma noventa y dos, muy por encima del objetivo de cero coma setenta y cinco. A la derecha ven el flujo completo del usuario: inicia sesión, elige la fruta, toma la foto, recibe el diagnóstico, lo califica, y puede ver su historial, incluso sin internet.

## Slide 4 — Plan de pruebas

Vamos al plan de pruebas, que es el primer criterio de esta evaluación. Diseñé cincuenta y siete casos de prueba automatizados: treinta y ocho para el backend y diecinueve para la aplicación Android. Y los organicé en cuatro tipos, porque no todas las pruebas verifican lo mismo. Las pruebas de validación responden a la pregunta: ¿estoy construyendo el sistema correcto? Es decir, si cumple los requisitos. Por ejemplo, que al enviar una imagen el sistema devuelva el diagnóstico correcto. Las de verificación responden: ¿lo estoy construyendo correctamente? Y miran atributos de calidad como el rendimiento o la precisión del modelo. Las de seguridad las basé en OWASP, que es el estándar de la industria para seguridad en aplicaciones. Y las operacionales verifican que el sistema funcione en su entorno. Del lado del backend, veintiuno de esos casos verifican específicamente el estado de madurez de la fruta: que cada detección se traduzca en el estado, color y recomendación correctos. Un punto importante es la base de datos de pruebas: no uso la base real, uso una base SQLite en memoria que se crea y se destruye en cada corrida. Esto aísla cada prueba, es rápido, y no expone datos reales de usuarios.

## Slide 5 — Aplicación y resultados

Acá están los resultados de aplicar ese plan. Las cincuenta y siete pruebas pasan al cien por ciento; las ejecuté hoy. El backend con pytest: treinta y ocho de treinta y ocho. La aplicación Android con MockK y JUnit: diecinueve de diecinueve. Además agregué integración continua: configuré un flujo en GitHub Actions que ejecuta toda la suite de pruebas cada vez que subo un cambio. Así, si algo rompe una prueba, me entero de inmediato y no integro código defectuoso. En cuanto a calidad, el modelo cumple su objetivo con cero coma noventa y dos de precisión, pesa solo cinco coma dos megabytes, y la aplicación compila e instala sin errores. En resumen: todos los componentes están cubiertos y verificados.

## Slide 6 — Mejoras al producto

Este es, para mí, el punto más importante: las mejoras. Y quiero destacar algo: estas mejoras no son arbitrarias. Cada una nace de un resultado de las pruebas o de una auditoría de seguridad que hice con OWASP. Las mapeé a los cinco estándares de calidad que pide la rúbrica. En seguridad, que fue el foco: descubrí que la clave secreta de los tokens estaba escrita en el código, que la información viajaba sin cifrar, y que el token se guardaba sin cifrar en el teléfono. Corregí las tres cosas. Ahora la clave va por variable de entorno, la comunicación es por HTTPS, y el token se guarda cifrado con AES de doscientos cincuenta y seis bits. En usabilidad, rediseñé toda la interfaz con Material Design tres, incluyendo modo oscuro e íconos vectoriales. En corrección, dejé toda la suite de pruebas y la compilación en verde después de integrar las funciones nuevas. En completitud, integré y probé de extremo a extremo la autenticación y el sistema de calificación. Y en pertinencia, las recomendaciones están ajustadas al dominio agrícola. Cada una de estas mejoras tiene un commit que la respalda, así que son completamente trazables.

## Slide 7 — Seguridad (OWASP)

Quiero profundizar un momento en seguridad, porque se trata de proteger los datos personales del usuario. Apliqué OWASP punto por punto: las contraseñas se guardan con un hash de bcrypt, nunca en texto plano. Los endpoints están protegidos con tokens JWT. La comunicación va cifrada por HTTPS, eso es el cifrado en tránsito. Y el token se guarda cifrado en el dispositivo, eso es el cifrado en reposo. Y acá hay un punto de ética que quiero mencionar. Estuve tentado de mostrarle al usuario un mensaje tipo cifrado de extremo a extremo, como WhatsApp. Pero decidí no hacerlo, porque sería falso: mi servidor necesita leer la imagen para procesarla. Sería engañar al usuario. Así que uso un mensaje veraz: tus datos viajan cifrados. La honestidad con el usuario también es parte de la calidad.

## Slide 8 — Conclusión

Para concluir. MaduraApp es hoy un producto funcional, probado y seguro. Cincuenta y siete de cincuenta y siete pruebas en verde, quince mejoras trazables a los estándares de calidad, y los datos personales protegidos con cifrado y hashing. De hecho, lo probé en producción: desplegué el backend en una instancia de AWS, con Docker y HTTPS, y escaneé un plátano real que diagnosticó como óptimo correctamente. Y soy honesto con lo que queda pendiente: el despliegue, por ser un laboratorio académico, es temporal; falta automatizar las pruebas de extremo a extremo, y obtener su aprobación formal del plan de pruebas en esta misma defensa.

## Slide 9 — Cierre / Preguntas

Eso es todo de mi parte. Muchas gracias por su atención. Quedo atento a sus preguntas.

