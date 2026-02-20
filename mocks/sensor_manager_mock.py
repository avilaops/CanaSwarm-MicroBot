#!/usr/bin/env python3
"""
CanaSwarm-MicroBot - Sensor Manager Mock

Gerencia sensores do robô (GPS, IMU, LIDAR, câmeras, etc)
"""

import random
from datetime import datetime
from typing import Dict, List


class SensorManager:
    """Gerenciador de sensores do MicroBot"""
    
    def __init__(self, robot_id: str):
        self.robot_id = robot_id
        self.sensors_status = {}
        self.sensor_readings = []
    
    def initialize_sensors(self) -> Dict:
        """Inicializa todos os sensores"""
        print(f"🔧 {self.robot_id} - Inicializando sensores...")
        
        sensors = {
            'gps': {'status': 'active', 'accuracy_m': 0.5, 'satellites': 12},
            'imu': {'status': 'active', 'calibration': 'ok'},
            'lidar': {'status': 'active', 'range_m': 50, 'resolution_deg': 0.25},
            'camera_front': {'status': 'active', 'resolution': '1920x1080', 'fps': 30},
            'camera_rear': {'status': 'active', 'resolution': '1920x1080', 'fps': 30},
            'fuel_sensor': {'status': 'active', 'type': 'ultrasonic'},
            'battery_monitor': {'status': 'active', 'voltage_range': '20-28V'},
            'blade_encoder': {'status': 'active', 'rpm_range': '0-2000'},
            'hopper_weight': {'status': 'active', 'capacity_kg': 500}
        }
        
        self.sensors_status = sensors
        
        for sensor_name, sensor_data in sensors.items():
            status_icon = "✅" if sensor_data['status'] == 'active' else "❌"
            print(f"   {status_icon} {sensor_name}: {sensor_data['status']}")
        
        print(f"\n✅ {len(sensors)} sensores inicializados\n")
        return sensors
    
    def read_gps(self, actual_position: Dict = None) -> Dict:
        """Lê posição GPS (com ruído simulado)"""
        if actual_position is None:
            # Posição padrão se não fornecida
            actual_position = {'lat': -22.7145, 'lon': -47.6489}
        
        # Adiciona ruído GPS (0.5m de precisão)
        noise_lat = random.uniform(-0.000005, 0.000005)  # ~0.5m
        noise_lon = random.uniform(-0.000005, 0.000005)
        
        reading = {
            'timestamp': datetime.now().isoformat(),
            'lat': actual_position['lat'] + noise_lat,
            'lon': actual_position['lon'] + noise_lon,
            'altitude_m': 550 + random.uniform(-2, 2),
            'accuracy_m': 0.5,
            'satellites': random.randint(10, 14),
            'fix_quality': 'rtk'  # Real-Time Kinematic (precisão cm)
        }
        
        return reading
    
    def read_imu(self) -> Dict:
        """Lê dados do IMU (acelerômetro, giroscópio, magnetômetro)"""
        reading = {
            'timestamp': datetime.now().isoformat(),
            'acceleration': {
                'x_m_s2': random.uniform(-0.5, 0.5),
                'y_m_s2': random.uniform(-0.5, 0.5),
                'z_m_s2': 9.81 + random.uniform(-0.1, 0.1)
            },
            'gyroscope': {
                'roll_deg_s': random.uniform(-2, 2),
                'pitch_deg_s': random.uniform(-2, 2),
                'yaw_deg_s': random.uniform(-5, 5)
            },
            'orientation': {
                'roll_deg': random.uniform(-5, 5),
                'pitch_deg': random.uniform(-5, 5),
                'yaw_deg': random.uniform(85, 95)  # ~90° (leste)
            },
            'temperature_c': 35 + random.uniform(-5, 5)
        }
        
        return reading
    
    def read_lidar(self) -> Dict:
        """Lê dados do LIDAR (obstáculos)"""
        # Simula detecção de obstáculos
        num_obstacles = random.randint(0, 3)
        obstacles = []
        
        for i in range(num_obstacles):
            obstacles.append({
                'distance_m': random.uniform(5, 50),
                'angle_deg': random.uniform(0, 360),
                'size_m': random.uniform(0.3, 2.0)
            })
        
        reading = {
            'timestamp': datetime.now().isoformat(),
            'obstacles_count': num_obstacles,
            'obstacles': obstacles,
            'scan_rate_hz': 10,
            'range_m': 50
        }
        
        return reading
    
    def read_harvest_sensors(self, is_harvesting: bool = False) -> Dict:
        """Lê sensores de colheita"""
        if is_harvesting:
            blade_rpm = random.uniform(1150, 1250)
            conveyor_speed = random.uniform(1.4, 1.6)
            harvest_rate = random.uniform(170, 190)
        else:
            blade_rpm = 0
            conveyor_speed = 0
            harvest_rate = 0
        
        reading = {
            'timestamp': datetime.now().isoformat(),
            'blade': {
                'rpm': blade_rpm,
                'vibration_mm_s': random.uniform(0.5, 2.0) if is_harvesting else 0,
                'temperature_c': 45 + random.uniform(-10, 10) if is_harvesting else 25
            },
            'conveyor': {
                'speed_m_s': conveyor_speed,
                'load_percent': random.uniform(50, 90) if is_harvesting else 0
            },
            'harvest_rate_kg_min': harvest_rate,
            'hopper_fill_percent': random.uniform(0, 100)
        }
        
        return reading
    
    def read_fuel_battery(self) -> Dict:
        """Lê níveis de combustível e bateria"""
        reading = {
            'timestamp': datetime.now().isoformat(),
            'fuel': {
                'level_percent': random.uniform(90, 100),
                'consumption_rate_l_h': random.uniform(8, 12)
            },
            'battery': {
                'voltage_v': random.uniform(24.0, 24.8),
                'current_a': random.uniform(5, 15),
                'temperature_c': random.uniform(30, 45)
            }
        }
        
        return reading
    
    def collect_all_sensors(self, actual_position: Dict = None, is_harvesting: bool = False) -> Dict:
        """Coleta leitura de todos os sensores"""
        reading = {
            'timestamp': datetime.now().isoformat(),
            'robot_id': self.robot_id,
            'gps': self.read_gps(actual_position),
            'imu': self.read_imu(),
            'lidar': self.read_lidar(),
            'harvest': self.read_harvest_sensors(is_harvesting),
            'fuel_battery': self.read_fuel_battery()
        }
        
        self.sensor_readings.append(reading)
        return reading
    
    def display_sensor_reading(self, reading: Dict):
        """Exibe leitura de sensores em formato dashboard"""
        print("\n" + "="*70)
        print("📡 LEITURA DE SENSORES")
        print("="*70)
        
        # GPS
        gps = reading['gps']
        print(f"\n📍 GPS:")
        print(f"   Posição: ({gps['lat']:.6f}, {gps['lon']:.6f})")
        print(f"   Altitude: {gps['altitude_m']:.1f}m")
        print(f"   Precisão: {gps['accuracy_m']}m ({gps['satellites']} satélites)")
        
        # IMU
        imu = reading['imu']
        print(f"\n🧭 IMU:")
        print(f"   Orientação: Roll {imu['orientation']['roll_deg']:.1f}° | Pitch {imu['orientation']['pitch_deg']:.1f}° | Yaw {imu['orientation']['yaw_deg']:.1f}°")
        print(f"   Aceleração Z: {imu['acceleration']['z_m_s2']:.2f} m/s²")
        
        # LIDAR
        lidar = reading['lidar']
        print(f"\n🔍 LIDAR:")
        print(f"   Obstáculos detectados: {lidar['obstacles_count']}")
        if lidar['obstacles']:
            for i, obs in enumerate(lidar['obstacles'], 1):
                print(f"      {i}. Distância: {obs['distance_m']:.1f}m | Ângulo: {obs['angle_deg']:.0f}°")
        
        # Colheita
        harvest = reading['harvest']
        print(f"\n🌾 COLHEITA:")
        print(f"   Lâmina: {harvest['blade']['rpm']:.0f} RPM")
        print(f"   Esteira: {harvest['conveyor']['speed_m_s']:.1f} m/s")
        print(f"   Taxa de colheita: {harvest['harvest_rate_kg_min']:.0f} kg/min")
        print(f"   Hopper: {harvest['hopper_fill_percent']:.1f}%")
        
        # Combustível/Bateria
        fb = reading['fuel_battery']
        print(f"\n🔋 ENERGIA:")
        print(f"   Combustível: {fb['fuel']['level_percent']:.1f}%")
        print(f"   Bateria: {fb['battery']['voltage_v']:.1f}V")


if __name__ == "__main__":
    print("📡 CanaSwarm-MicroBot - Sensor Manager Mock\n")
    print("="*70)
    
    # Inicializa gerenciador de sensores
    sensor_mgr = SensorManager("MICROBOT-001")
    
    # Inicializa sensores
    sensors = sensor_mgr.initialize_sensors()
    
    # Coleta leitura completa
    print("📊 Coletando leitura de sensores...")
    reading = sensor_mgr.collect_all_sensors(
        actual_position={'lat': -22.7145, 'lon': -47.6489},
        is_harvesting=True
    )
    
    # Exibe leitura
    sensor_mgr.display_sensor_reading(reading)
    
    print("\n" + "="*70)
    print("✅ SENSORES OPERACIONAIS")
    print("="*70)
    print(f"\n💡 {len(sensors)} sensores ativos e funcionando\n")
