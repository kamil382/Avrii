## Dashboard

![Dashboard AVRII](images/avrii1.png)
![Dashboard AVRII](images/avrii2.png)
![Dashboard AVRII](images/avrii3.png)



# AVRII Modbus Inverter iHomeTech Edition

Integracja falowników AVRII z Home Assistant przez Modbus TCP.

## Funkcje

- odczyt parametrów falownika
- moc PV
- napięcia
- prądy
- produkcja energii
- stan baterii
- komunikacja Modbus TCP
- konfiguracja przez UI Home Assistant

## Instalacja przez HACS

1. Otwórz HACS
2. Przejdź do Integrations
3. Wyszukaj AVRII
4. Zainstaluj integrację
5. Uruchom ponownie Home Assistant
6. Dodaj integrację AVRII

## Konfiguracja

Integracja jest konfigurowana z poziomu Home Assistant.

```yaml
type: custom:sunsynk-power-flow-card
cardstyle: full
show_solar: true
battery:
  shutdown_soc: 20
  show_daily: true
  show_absolute: true
  auto_scale: false
  energy: 10000
  soc_end_of_charge: 100
  remaining_energy_to_shutdown: false
solar:
  show_daily: true
  mppts: 2
  pv1_name: PV1
  pv2_name: PV2
  auto_scale: false
  display_mode: 1
  invert_flow: false
  pv3_name: Wiatrak
load:
  show_daily: true
  load1_name: Bojler
  load1_icon: mdi:water-boiler
  load1_max_threshold: 1
  dynamic_icon: true
  invert_load: false
  dynamic_colour: true
  auto_scale: false
  load2_name: jacuzzi
  load2_icon: mdi:pool
  load2_max_threshold: 1
  additional_loads: 1
  load3_name: korytarz
  load3_max_threshold: 1
  load3_icon: mdi:air-conditioner
  load3_switch: climate.klimatyzator_korytarz
  load2_switch: switch.layzspa_wifi_controller_layzspa_heat_regulation
  load4_name: salon
  load4_icon: mdi:air-conditioner
  load4_switch: climate.klimatyzator_salon
  load4_max_threshold: 1
  max_colour: "#fff700"
  colour: "#8f8eb8"
  invert_flow: false
  show_aux: false
  load1_switch: select.energy_monitoring_plug_with_display_switch_state
grid:
  show_daily_buy: true
  show_daily_sell: true
  show_nonessential: false
  auto_scale: false
  invert_grid: false
  show_absolute: false
entities:
  use_timer_248: switch.sunsynk_toggle_system_timer
  priority_load_243: switch.sunsynk_toggle_priority_load
  load_frequency_192: sensor.avrii_l1_frequency
  inverter_current_164: sensor.sunsynk_inverter_current
  inverter_power_175: sensor.avrii_total_watt_of_backup
  grid_connected_status_194: binary_sensor.sunsynk_grid_connected_status
  inverter_status_59: sensor.sunsynk_overall_state
  day_battery_charge_70: sensor.avrii_battery_today_charge_energy
  day_battery_discharge_71: sensor.avrii_battery_today_discharge_energy
  battery_voltage_183: sensor.avrii_battery_voltage
  battery_soc_184: sensor.avrii_battery_soc
  battery_power_190: sensor.avrii_battery_power
  battery_current_191: sensor.avrii_battery_current
  grid_power_169: sensor.avrii_total_watt_of_backup
  day_grid_import_76: sensor.avrii_today_import_energy
  day_grid_export_77: sensor.avrii_today_export_energy
  day_load_energy_84: sensor.avrii_today_load_energy
  essential_power: sensor.avrii_total_watt_of_load
  nonessential_power: none
  day_pv_energy_108: sensor.avrii_today_energy
  pv1_power_186: sensor.avrii_mppt1_power
  pv2_power_187: sensor.avrii_mppt2_power
  pv1_voltage_109: sensor.avrii_mppt1_voltage
  pv1_current_110: sensor.avrii_mppt1_current
  pv2_voltage_111: sensor.avrii_mppt2_voltage
  pv2_current_112: sensor.avrii_mppt2_current
  battery_temp_182: sensor.avrii_battery_temperature
  grid_ct_power_172: sensor.avrii_total_watt_of_grid
  essential_load1: sensor.energy_monitoring_plug_with_display_moc
  essential_load1_extra: sensor.bojler31_temperatura_bojler
  dc_transformer_temp_90: sensor.avrii_battery_average_cell_temperature
  radiator_temp_91: sensor.avrii_inner_temperature
  essential_load2: null
  essential_load2_extra: null
  essential_load3: null
  essential_load4: null
  essential_load4_extra: null
  essential_load3_extra: null
  pv3_power_188: null
  inverter_voltage_154: sensor.avrii_l1_n_phase_voltage_of_grid
  inverter_voltage_L2: sensor.avrii_l2_n_phase_voltage_of_grid
  inverter_voltage_L3: sensor.avrii_l3_n_phase_voltage_of_grid
large_font: true
inverter:
  three_phase: true
  autarky: energy
  navigate: local
  modern: false
  model: ferroamp
center_no_grid: false
show_grid: true
show_battery: true
wide: false
dynamic_line_width: false
card_height: ""


```


## Licencja

Apache License 2.0
