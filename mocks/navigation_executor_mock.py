#!/usr/bin/env python3
"""
CanaSwarm-MicroBot - Navigation Executor Mock

Executa navegação usando waypoints com controle de velocidade e ações
"""

import math
from typing import Dict, Tuple, List


class NavigationExecutor:
    """Executor de navegação para robô autônomo"""
    
    def __init__(self, robot_id: str):
        self.robot_id = robot_id
        self.current_position = None
        self.current_heading_deg = 0
        self.current_velocity_m_s = 0
        self.total_distance_m = 0
    
    def calculate_distance(self, pos1: Dict, pos2: Dict) -> float:
        """
        Calcula distância entre dois pontos GPS usando fórmula de Haversine
        
        Args:
            pos1: {'lat': float, 'lon': float}
            pos2: {'lat': float, 'lon': float}
        
        Returns:
            Distância em metros
        """
        R = 6371000  # Raio da Terra em metros
        
        lat1 = math.radians(pos1['lat'])
        lat2 = math.radians(pos2['lat'])
        delta_lat = math.radians(pos2['lat'] - pos1['lat'])
        delta_lon = math.radians(pos2['lon'] - pos1['lon'])
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1) * math.cos(lat2) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance
    
    def calculate_bearing(self, pos1: Dict, pos2: Dict) -> float:
        """
        Calcula bearing (azimute) de pos1 para pos2
        
        Args:
            pos1: Posição inicial
            pos2: Posição final
        
        Returns:
            Bearing em graus (0-360, onde 0=Norte, 90=Leste)
        """
        lat1 = math.radians(pos1['lat'])
        lat2 = math.radians(pos2['lat'])
        delta_lon = math.radians(pos2['lon'] - pos1['lon'])
        
        x = math.sin(delta_lon) * math.cos(lat2)
        y = (math.cos(lat1) * math.sin(lat2) -
             math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon))
        
        bearing = math.atan2(x, y)
        bearing_deg = math.degrees(bearing)
        bearing_deg = (bearing_deg + 360) % 360
        
        return bearing_deg
    
    def navigate_to_waypoint(self, waypoint: Dict, start_pos: Dict = None) -> Dict:
        """
        Navega para um waypoint
        
        Args:
            waypoint: Waypoint destino
            start_pos: Posição inicial (se None, usa current_position)
        
        Returns:
            Resultado da navegação
        """
        if start_pos is None:
            start_pos = self.current_position
        
        if start_pos is None:
            raise ValueError("Posição inicial não definida")
        
        # Calcula distância e bearing
        distance_m = self.calculate_distance(start_pos, waypoint)
        bearing_deg = self.calculate_bearing(start_pos, waypoint)
        
        # Calcula tempo estimado
        target_velocity = waypoint.get('velocity_m_s', 1.0)
        time_seconds = distance_m / target_velocity if target_velocity > 0 else 0
        
        # Atualiza estado
        self.current_position = waypoint
        self.current_heading_deg = bearing_deg
        self.current_velocity_m_s = target_velocity
        self.total_distance_m += distance_m
        
        return {
            'waypoint_id': waypoint.get('waypoint_id', 'unknown'),
            'distance_m': distance_m,
            'bearing_deg': bearing_deg,
            'target_velocity_m_s': target_velocity,
            'estimated_time_s': time_seconds,
            'action': waypoint.get('action', 'navigate'),
            'arrival_position': self.current_position
        }
    
    def execute_navigation_plan(self, navigation_plan: Dict) -> List[Dict]:
        """
        Executa plano de navegação completo
        
        Args:
            navigation_plan: Plano com start_position e waypoints
        
        Returns:
            Lista de resultados de cada segmento
        """
        # Define posição inicial
        self.current_position = navigation_plan['start_position']
        self.current_heading_deg = navigation_plan['start_position'].get('heading_deg', 0)
        self.total_distance_m = 0
        
        results = []
        
        for waypoint in navigation_plan['waypoints']:
            result = self.navigate_to_waypoint(waypoint)
            results.append(result)
        
        return results
    
    def display_navigation_summary(self, results: List[Dict]):
        """Exibe resumo da navegação"""
        print("\n" + "="*70)
        print("🗺️  RESUMO DE NAVEGAÇÃO")
        print("="*70)
        
        print(f"\n📍 WAYPOINTS NAVEGADOS: {len(results)}")
        
        total_distance = sum(r['distance_m'] for r in results)
        total_time = sum(r['estimated_time_s'] for r in results)
        
        for i, result in enumerate(results, 1):
            action_icon = "🌾" if 'harvest' in result['action'] else "🔄" if 'turn' in result['action'] else "📍"
            
            print(f"\n{action_icon} {i}. {result['waypoint_id']} - {result['action'].upper()}")
            print(f"   Distância: {result['distance_m']:.1f}m")
            print(f"   Bearing: {result['bearing_deg']:.1f}°")
            print(f"   Velocidade: {result['target_velocity_m_s']:.1f} m/s")
            print(f"   Tempo: {result['estimated_time_s']:.1f}s")
        
        print(f"\n📊 TOTAIS:")
        print(f"   Distância total: {total_distance:.1f}m")
        print(f"   Tempo total: {total_time/60:.1f} minutos")
        print(f"   Velocidade média: {total_distance/total_time:.2f} m/s")


if __name__ == "__main__":
    print("🗺️  CanaSwarm-MicroBot - Navigation Executor Mock\n")
    print("="*70)
    
    # Inicializa navegador
    navigator = NavigationExecutor("MICROBOT-001")
    
    # Carrega plano de navegação de exemplo
    import json
    from pathlib import Path
    
    command_file = Path(__file__).parent / "example_robot_commands.json"
    with open(command_file, 'r', encoding='utf-8') as f:
        command = json.load(f)
    
    navigation_plan = command['navigation_plan']
    
    print(f"\n📋 Executando plano de navegação:")
    print(f"   Posição inicial: ({navigation_plan['start_position']['lat']:.4f}, {navigation_plan['start_position']['lon']:.4f})")
    print(f"   Waypoints: {len(navigation_plan['waypoints'])}")
    print(f"   Distância planejada: {navigation_plan['path_length_meters']}m")
    
    # Executa navegação
    results = navigator.execute_navigation_plan(navigation_plan)
    
    # Exibe resultados
    navigator.display_navigation_summary(results)
    
    print("\n" + "="*70)
    print("✅ NAVEGAÇÃO COMPLETA")
    print("="*70)
    print(f"\n💡 Robô chegou ao destino\n")
