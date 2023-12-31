﻿# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def plot_trajectory(position_x, position_y, theta):
    plt.figure(figsize=(10, 6))
    
    # Траектория движения
    plt.plot(position_x, position_y, label='Траектория', color='blue')

    # Начальная и конечная точки
    plt.scatter(position_x[0], position_y[0], color='green', label='Начало')
    plt.scatter(position_x[-1], position_y[-1], color='red', label='Конец')

    # Ориентация в ключевых точках
    for i in range(0, len(position_x), len(position_x)//20):  # Каждая 20-я точка
        end_x = position_x[i] + np.cos(theta[i]) * 0.1  # Уменьшите масштаб, если необходимо
        end_y = position_y[i] + np.sin(theta[i]) * 0.1
        plt.arrow(position_x[i], position_y[i], end_x - position_x[i], end_y - position_y[i],
                  head_width=0.05, head_length=0.1, fc='red', ec='red')

    plt.title('Визуализация траектории движения')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.legend()
    plt.axis('equal')  # Установка одинакового масштаба для осей X и Y
    plt.grid(True)
    plt.show()

def kalman_filter(z, dt):
    # Инициализация переменных
    x = np.array([[0.0, 0.0, 0.0, 0.0]]).T  # состояние (x, y, vx, vy)
    P = np.eye(4)  # оценка ошибки ковариации
    F = np.array([[1, 0, dt, 0],
                  [0, 1, 0, dt],
                  [0, 0, 1, 0],
                  [0, 0, 0, 1]])  # матрица перехода состояния
    Q = np.eye(4) * 0.1  # ковариация шума процесса
    H = np.array([[1, 0, 0, 0],
                  [0, 1, 0, 0]])  # матрица наблюдения
    R = np.eye(2) * 1  # ковариация шума наблюдения
    
    x_est = np.zeros((len(z), 4))  # Массив для хранения оценок положения
    
    for i in range(len(z)):
        # Прогноз
        x = np.dot(F, x)
        P = np.dot(F, np.dot(P, F.T)) + Q
        
        # Обновление
        S = np.dot(H, np.dot(P, H.T)) + R
        K = np.dot(P, np.dot(H.T, np.linalg.inv(S)))
        y = z[i].reshape(2, 1) - np.dot(H, x)
        x += np.dot(K, y)
        P = P - np.dot(K, np.dot(H, P))
        
        x_est[i] = x.T
    
    return x_est

    
# Чтение данных из файла Excel
file_path = 'KRAYOT_Smartphone.xlsx'  # Замените на путь к вашему файлу
data = pd.read_excel(file_path)

# Извлечение данных
time = data['Timestamp'].to_numpy()  # Предполагается, что Timestamp в секундах
acc_x = data['accX'].to_numpy()
acc_y = data['accY'].to_numpy()
gyro_z = data['GyrZ'].to_numpy()  # Угловая скорость вокруг оси Z

# Инициализация переменных для хранения скоростей и положений
velocity_x = np.zeros_like(acc_x)
velocity_y = np.zeros_like(acc_y)
position_x = np.zeros_like(acc_x)
position_y = np.zeros_like(acc_y)
theta = np.zeros_like(gyro_z)  # Угол ориентации

# Интегрирование для получения скорости, положения и ориентации
for i in range(1, 250):
    dt = time[i] - time[i-1]
    theta[i] = theta[i-1] + gyro_z[i] * dt  # Интегрирование угловой скорости для получения угла

    # Преобразование локального ускорения в глобальное с использованием угла ориентации
    global_acc_x = acc_x[i] * np.cos(theta[i]) - acc_y[i] * np.sin(theta[i])
    global_acc_y = acc_x[i] * np.sin(theta[i]) + acc_y[i] * np.cos(theta[i])

    # Интегрирование ускорения для получения скорости и положения
    velocity_x[i] = velocity_x[i-1] + global_acc_x * dt
    velocity_y[i] = velocity_y[i-1] + global_acc_y * dt
    position_x[i] = position_x[i-1] + velocity_x[i] * dt
    position_y[i] = position_y[i-1] + velocity_y[i] * dt

# Создание DataFrame для сохранения результатов
results = pd.DataFrame({
    'Time': time,
    'Position_X': position_x,
    'Position_Y': position_y,
    'Velocity_X': velocity_x,
    'Velocity_Y': velocity_y,
    'Orientation_Theta': theta
})

# Сохранение данных в CSV файл
csv_file_path = 'output.csv'  # Укажите нужный путь для сохранения файла
results.to_csv(csv_file_path, index=False)

print(csv_file_path)

#plot_trajectory(position_x, position_y, theta)
# Подготовка данных для фильтра Калмана
measurements = np.vstack((position_x, position_y)).T  # измерения

# Применение фильтра Калмана
kalman_positions = kalman_filter(measurements, time[1] - time[0])

# Визуализация
plt.figure(figsize=(15, 7))

# Исходная траектория
plt.subplot(1, 2, 1)
plt.plot(position_x, position_y, label='Исходная траектория', color='blue')
plt.title('Исходная траектория')
plt.xlabel('X')
plt.ylabel('Y')
plt.legend()
plt.grid(True)

# Оцененная траектория с использованием фильтра Калмана
plt.subplot(1, 2, 2)
plt.plot(kalman_positions[:, 0], kalman_positions[:, 1], label='Оценка фильтра Калмана', color='red')
plt.title('Траектория с использованием фильтра Калмана')
plt.xlabel('X')
plt.ylabel('Y')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()