import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from lightgbm import LGBMClassifier

# Загрузка датасета и подготовка данных
import statsmodels.api as sm
df = sm.datasets.fair.load_pandas().data

# Добавление новых признаков для анкеты
df['age_marriage_ratio'] = df['age'] / (df['yrs_married'] + 0.1)  # чтобы не делить на 0
df['is_high_education'] = (df['educ'] >= 16).astype(int)
df['is_high_religious'] = (df['religious'] >= 3).astype(int)

# Целевая переменная
df['had_affair'] = (df['affairs'] > 0).astype(int)

# Признаки
X = df.drop(columns=['rate_marriage', 'affairs', 'had_affair'])
y = df['had_affair']

# Обучение модели
model = LGBMClassifier(
    random_state=42,
    n_estimators=100,
    max_depth=10,
    learning_rate=0.01,
    num_leaves=50,
    is_unbalance=True,
    verbose=-1  # Отключение вывода логов LightGBM
)
model.fit(X, y)

# Анкета для пользователя
def ask_user_input():
    print("🔍 Оцените ваш брак и поведение вашей жены:")
    
    questions = {
        "age": "Возраст вашей жены (в годах): ",
        "yrs_married": "Сколько лет вы в браке? (например, 3.5): ",
        "children": "Сколько у вас детей? (0, 1, 2...): ",
        "religious": """Уровень религиозности вашей жены:
        1 — Не религиозна
        2 — Немного религиозна
        3 — Религиозна
        4 — Очень религиозна
Ваш выбор: """,
        "educ": """Уровень образования вашей жены (в годах обучения):
        12 — Среднее образование
        14 — Бакалавриат
        16 — Магистратура
        18+ — Аспирантура
Ваш выбор: """,
        "occupation": """Сфера деятельности вашей жены:
        1 — Студентка
        2 — Рабочая (синий воротничок)
        3 — Служащая / офисная работа
        4 — Техническая профессия
        5 — Менеджер / руководитель
        6 — Профессионал (врач, юрист и т.д.)
Ваш выбор: """,
        "occupation_husb": """Ваша собственная сфера деятельности:
        1 — Студент
        2 — Рабочий
        3 — Служащий / офис
        4 — Технарь
        5 — Менеджер
        6 — Профессия высокого уровня
Ваш выбор: """
    }

    user_data = {}
    for key, question in questions.items():
        while True:
            try:
                val = float(input(question))
                user_data[key] = val
                break
            except ValueError:
                print("Пожалуйста, введите число.")
    return pd.DataFrame([user_data])

# Ввод данных пользователем
user_df = ask_user_input()

# Преобразуем введенные данные в нужный формат
user_df['age_marriage_ratio'] = user_df['age'] / (user_df['yrs_married'] + 0.1)
user_df['is_high_education'] = (user_df['educ'] >= 16).astype(int)
user_df['is_high_religious'] = (user_df['religious'] >= 3).astype(int)

# Предсказание
y_pred_prob = model.predict_proba(user_df)[:, 1]
threshold = 0.35
prediction = (y_pred_prob > threshold).astype(int)

# Вывод результата
print("\n🔍 Результат анализа:")
if prediction == 1:
    print(f"⚠️ Модель предсказывает высокую вероятность измены. Вероятность: {y_pred_prob[0]:.2f}")
else:
    print(f"✅ Модель не предсказывает измену. Вероятность: {y_pred_prob[0]:.2f}")

# Визуализация важности признаков
feature_importance = model.feature_importances_
features = X.columns

# График важности признаков
plt.figure(figsize=(10, 6))
sns.barplot(x=feature_importance, y=features)
plt.title('Важность признаков для предсказания')
plt.xlabel('Важность')
plt.ylabel('Признаки')
plt.show()

# График вероятности
plt.figure(figsize=(6, 6))
sns.histplot(y_pred_prob, bins=20, kde=True)
plt.axvline(x=y_pred_prob[0], color='r', linestyle='--', label=f'Предсказанная вероятность: {y_pred_prob[0]:.2f}')
plt.title('Распределение вероятности для измены')
plt.xlabel('Вероятность измены')
plt.ylabel('Частота')
plt.legend()
plt.show()
