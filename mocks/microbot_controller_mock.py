#!/usr/bin/env python3
"""
CanaSwarm-MicroBot - MicroBot Controller Mock

Controlador principal do robô autônomo de colheita
"""

import json
import time
from pathlib import Path
from typing import Dict, List
from datetime import datetime


class MicrobotController:
    """Controlador principal de um MicroBot individual"""
    
    def __init__(self, robot_id: str):
        self.robot_id = robot_id
        self.status = "idle"
        self.current_mission = None
        self.current_position = None
        self.fuel_level_percent = 100
        self.battery_voltage_v = 24.5
        self.hopper_fill_percent = 0
        self.harvest_rate_kg_min = 0
        self.telemetry_history = []
    
    def load_command(self, filepath: str) -> Dict:
        """Carrega comando de missão do CanaSwarm-Core"""
        print(f"🤖 {self.robot_id} - Carregando comando: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            command = json.load(f)
        
        # Valida se o comando é para este robô
        if command['robot_id'] != self.robot_id:
            raise ValueError(f"Comando destinado a {command['robot_id']}, não a {self.robot_id}")
        
        self.current_mission = command
        self.current_position = command['navigation_plan']['start_position']
        
        print(f"✅ Comando carregado: {command['command_id']}")
        print(f"   Missão: {command['mission_id']}")
        print(f"   Zona: {command['zone_assignment']['zone_name']} ({command['zone_assignment']['area_ha']} ha)")
        print(f"   Waypoints: {len(command['navigation_plan']['waypoints'])}")
        print(f"   Duração estimada: {command['expected_results']['estimated_duration_hours']} horas\n")
        
        return command
    
    def validate_safety_conditions(self) -> List[str]:
        """Valida condições de segurança antes de iniciar"""
        issues = []
        limits = self.current_mission['safety_limits']
        
        # Verifica combustível
        if self.fuel_level_percent < limits['min_fuel_percent']:
            issues.append(f"⚠️  Combustível baixo: {self.fuel_level_percent}% (mínimo: {limits['min_fuel_percent']}%)")
        
        # Verifica bateria
        if self.battery_voltage_v < limits['min_battery_voltage_v']:
            issues.append(f"⚠️  Bateria baixa: {self.battery_voltage_v}V (mínimo: {limits['min_battery_voltage_v']}V)")
        
        # Verifica GPS (simulado)
        if self.current_position is None:
            issues.append("❌ Sinal GPS não disponível")
        
        return issues
    
    def execute_mission(self):
        """Executa missão completa"""
        if not self.current_mission:
            print("❌ Nenhuma missão carregada")
            return
        
        print(f"\n🚀 {self.robot_id} - INICIANDO MISSÃO")
        print("="*70)
        
        # Validação de segurança
        print("\n🔍 Validando condições de segurança...")
        safety_issues = self.validate_safety_conditions()
        
        if safety_issues:
            print("❌ MISSÃO ABORTADA - Problemas de segurança:")
            for issue in safety_issues:
                print(f"   {issue}")
            return
        else:
            print("✅ Todas as condições de segurança OK")
        
        # Configuração de colheita
        print(f"\n⚙️  Configurando parâmetros de colheita...")
        params = self.current_mission['harvest_parameters']
        print(f"   Altura de corte: {params['cutting_height_cm']} cm")
        print(f"   Velocidade da lâmina: {params['blade_speed_rpm']} RPM")
        print(f"   Velocidade da esteira: {params['conveyor_speed_m_s']} m/s")
        print(f"   Capacidade do hopper: {params['hopper_capacity_kg']} kg")
        
        # Navegação
        print(f"\n🗺️  Executando navegação...")
        self.status = "navigating"
        waypoints = self.current_mission['navigation_plan']['waypoints']
        
        for i, wp in enumerate(waypoints, 1):
            self._execute_waypoint(wp, i, len(waypoints))
            time.sleep(0.5)  # Simula tempo de navegação
        
        # Finalização
        self.status = "mission_completed"
        print(f"\n🎉 {self.robot_id} - MISSÃO CONCLUÍDA")
        self._generate_mission_report()
    
    def _execute_waypoint(self, waypoint: Dict, current: int, total: int):
        """Executa navegação para um waypoint"""
        # Simula navegação
        self.current_position = {
            'lat': waypoint['lat'],
            'lon': waypoint['lon'],
            'heading_deg': 90
        }
        
        # Simula consumo de combustível (0.5% por waypoint)
        self.fuel_level_percent -= 0.5
        
        # Simula enchimento de hopper durante colheita
        if waypoint['action'] in ['harvest', 'start_harvest']:
            self.hopper_fill_percent += 15
            self.harvest_rate_kg_min = 180
        elif waypoint['action'] == 'end_harvest':
            self.harvest_rate_kg_min = 0
        
        # Status
        action_icon = "🌾" if 'harvest' in waypoint['action'] else "🔄" if 'turn' in waypoint['action'] else "📍"
        
        print(f"   {action_icon} [{current}/{total}] WP {waypoint['waypoint_id']}: {waypoint['action']}")
        print(f"      Posição: ({waypoint['lat']:.4f}, {waypoint['lon']:.4f})")
        print(f"      Velocidade: {waypoint['velocity_m_s']} m/s")
        print(f"      Combustível: {self.fuel_level_percent:.1f}% | Hopper: {self.hopper_fill_percent:.1f}%")
        
        # Registra telemetria
        self._record_telemetry(waypoint)
    
    def _record_telemetry(self, waypoint: Dict):
        """Registra telemetria atual"""
        telemetry = {
            'timestamp': datetime.now().isoformat(),
            'position': self.current_position,
            'velocity_m_s': waypoint['velocity_m_s'],
            'fuel_level_percent': self.fuel_level_percent,
            'battery_voltage_v': self.battery_voltage_v,
            'hopper_fill_percent': self.hopper_fill_percent,
            'harvest_rate_kg_min': self.harvest_rate_kg_min,
            'status': self.status
        }
        self.telemetry_history.append(telemetry)
    
    def _generate_mission_report(self):
        """Gera relatório de missão"""
        print("\n" + "="*70)
        print("📊 RELATÓRIO DE MISSÃO")
        print("="*70)
        
        expected = self.current_mission['expected_results']
        
        print(f"\n🎯 RESULTADOS:")
        print(f"   Área colhida: {expected['area_to_harvest_ha']} ha")
        print(f"   Produção estimada: {expected['estimated_yield_tons']:,} toneladas")
        print(f"   Duração: {expected['estimated_duration_hours']} horas")
        print(f"   Receita estimada: R$ {expected['revenue_estimate_brl']:,}")
        
        print(f"\n🔋 CONSUMÍVEIS:")
        print(f"   Combustível final: {self.fuel_level_percent:.1f}%")
        print(f"   Bateria final: {self.battery_voltage_v:.1f}V")
        print(f"   Hopper final: {self.hopper_fill_percent:.1f}%")
        
        print(f"\n📡 TELEMETRIA:")
        print(f"   Registros coletados: {len(self.telemetry_history)}")
        print(f"   Waypoints navegados: {len(self.current_mission['navigation_plan']['waypoints'])}")
    
    def save_telemetry(self, output_dir: str = None):
        """Salva telemetria em arquivo"""
        if output_dir is None:
            output_dir = Path(__file__).parent
        else:
            output_dir = Path(output_dir)
        
        filename = f"telemetry_{self.robot_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = output_dir / filename
        
        data = {
            'robot_id': self.robot_id,
            'mission_id': self.current_mission['mission_id'],
            'command_id': self.current_mission['command_id'],
            'telemetry': self.telemetry_history,
            'final_status': {
                'fuel_level_percent': self.fuel_level_percent,
                'battery_voltage_v': self.battery_voltage_v,
                'hopper_fill_percent': self.hopper_fill_percent,
                'status': self.status
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Telemetria salva em: {filename}")
        return str(filepath)


if __name__ == "__main__":
    print("🤖 CanaSwarm-MicroBot - Controlador Mock\n")
    print("="*70)
    
    # Inicializa robô
    robot = MicrobotController("MICROBOT-001")
    
    # Carrega comando
    command_file = Path(__file__).parent / "example_robot_commands.json"
    robot.load_command(str(command_file))
    
    # Executa missão
    robot.execute_mission()
    
    # Salva telemetria
    robot.save_telemetry()
    
    print("\n" + "="*70)
    print("✅ EXECUÇÃO CONCLUÍDA")
    print("="*70)
    print("\n💡 Robô pronto para próxima missão\n")
