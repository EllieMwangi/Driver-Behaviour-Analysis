import pandas as pd
import numpy as np
from statistics import mean, mode
from sqlalchemy import create_engine
import pickle, os


class DailySummaries:
    def __init__(self,date):
        self.trip_summaries = self.TripSummaries(date)
        self.ids = self.trip_summaries.trip_ids

    # Returns daily summary
    def daily_summaries(self):
        average_speeds = []
        distances_covered = []
        periods_on_road = []
        fuel_amounts_consumed = []
        fuel_costs_incurred = []
        engine_idle_times = []
        behaviour_scores = []

        for trip in self.ids:
            trip_summary = self.trip_summaries.trip_analysis(trip)
            average_speeds.append(trip_summary['Average_speed'])
            distances_covered.append(trip_summary['Distance_covered'])
            periods_on_road.append(trip_summary['Time_spent_on_road'])
            fuel_amounts_consumed.append(trip_summary['Fuel_consumed'])
            fuel_costs_incurred.append(trip_summary['Estimated_fuel_cost'])
            engine_idle_times.append(trip_summary['Idle_engine_time'])
            if len(trip_summary['Driving_Behaviour']) == 14:
                behaviour_scores.append(1)
            else:
                behaviour_scores.append(-1)
        print(engine_idle_times)
        daily_summary = {'Average_speed_of_trips': mean(average_speeds),'Total_distance_covered':sum(distances_covered),
                         'Total_engine_idle_time':sum(engine_idle_times)/60,'Total_fuel_consumed':sum(fuel_amounts_consumed),
                         'Total_time_on_road':sum(periods_on_road),'Total_fuel_costs':sum(fuel_costs_incurred),'Number_of_trips':
                         len(self.ids),'Driving_Behaviour':mode(behaviour_scores)}

        return daily_summary

    def trip_ids(self):

        ids = self.ids
        trip_dict={}

        for x in ids:
            trip_dict['Trip ' + str(x)] = x

        return trip_dict

    class TripSummaries:
        def __init__(self, date):

            self.date = date
            db_url = 'sqlite:///' + os.path.abspath('myapp/envirocar.db')
            conn = create_engine(db_url)
            start_time = self.date + " " + "00:00:00.000000"
            end_time = self.date + " " + "23:59:59.999999"
            query = 'SELECT * FROM VehicleData WHERE Time >= ? and Time <= ?'
            self.data = pd.read_sql_query(query, conn, params=(start_time, end_time), parse_dates=['Time'])
            self.trip_ids = list(set(self.data.TripID.values))

        def behaviour_analysis(self, dataframe,trip_id):
            trip_data = dataframe[dataframe.TripID == trip_id]
            throttle_change_rate = np.diff(trip_data['Absolute Throttle Position'].values)
            print(throttle_change_rate)
            es_change_rate = np.diff(trip_data['Engine RPM'].values)
            engine_load = [x / 2.55 for x in trip_data['Vehicle Speed Sensor'].values]
            vs_change_rate = np.diff(trip_data['Vehicle Speed Sensor'].values)
            vehicle_speed_norm = [x / 220 for x in trip_data['Vehicle Speed Sensor'].values[
                                                   :len(trip_data['Vehicle Speed Sensor'].values) - 1]]
            engine_speed_norm = [x / 8000 for x in
                                 trip_data['Engine RPM'].values[:len(trip_data['Engine RPM'].values) - 1]]
            vs_es = pd.DataFrame({'vs_norm': vehicle_speed_norm, 'es_norm': engine_speed_norm})
            vs_es['rr_of_vs_and_es'] = vs_es.vs_norm / vs_es.es_norm
            maximum_change_tp = max(throttle_change_rate)
            maximum_change_es = max(es_change_rate)
            throttle_position_norm = [x / maximum_change_tp for x in throttle_change_rate]
            # len(throttle_position_norm)
            es_relative_norm = [x / maximum_change_es for x in es_change_rate]
            # len(es_relative_norm)
            tp_er = pd.DataFrame({'tp_norm': throttle_position_norm, 'er_norm': es_relative_norm})
            tp_er['rr_of_tp_and_es'] = tp_er.tp_norm / tp_er.er_norm
            feature_set = pd.DataFrame({'rr_of_vs_and_es':vs_es.rr_of_vs_and_es.values,'rr_of_tp_and_es':tp_er.rr_of_tp_and_es.values,
                                        'engine_load': engine_load[:-1]})
            feature_set = feature_set[~feature_set.isin([np.nan, np.inf, -np.inf]).any(1)]
            filename = os.path.abspath("analysis/behaviour_analysis.sav")
            loaded_model = pickle.load(open(filename, 'rb'))
            results = loaded_model.predict(feature_set).tolist()
            score = mode(results)
            if score == 1:
                return 'Fuel Efficient'
            else:
                return 'Not Fuel Efficient'

        def idle_time_calculator(self,speed_array):
            speed_values = speed_array
            idle_time_periods = []
            if (all(x == 0 for x in speed_values) and len(speed_values) > 0):
                idle_time_periods.append(5)

            # print(idle_time_periods)
            return idle_time_periods

        def engine_total_idle_time(self, dataframe):
            trip_data = dataframe.set_index('Time')
            trip_data = trip_data[trip_data['Vehicle Speed Sensor'] == 0]
            trip_data = trip_data[trip_data['Engine RPM'] > 0]
            idle_time = (trip_data['Vehicle Speed Sensor'].resample('5T').apply(self.idle_time_calculator)).sum()
            #Return idle_time in minutes
            return idle_time

        def mpg_calculator(self, dataframe):
            speed_val = dataframe['Vehicle Speed Sensor'].values
            mpg_val = [x * 7.718 * 0.354 for x in speed_val]
            mpg = mean(mpg_val)
            return mpg

        def trip_analysis(self, trip_id):
            trip_data = self.data[self.data.TripID == trip_id]
            #print(trip_data)
            #print(trip_data.Time.tail(1).values)
            time_spent_on_road = round(((trip_data.Time.tail(1).values - trip_data.Time.head(1).values)[0])/np.timedelta64(1,'h'),2)
            average_speed = round(mean(trip_data['Vehicle Speed Sensor'].values), 2)
            max_speed = max(trip_data['Vehicle Speed Sensor'].values)
            min_speed = min([x for x in trip_data['Vehicle Speed Sensor'].values if x != 0])
            distance_covered = round((average_speed * time_spent_on_road), 2)
            driver_behaviour = self.behaviour_analysis(trip_data,trip_id)
            idle_time = self.engine_total_idle_time(trip_data)
            fuel_consumed = round((self.mpg_calculator(trip_data)/distance_covered),2)
            estimated_fuel_cost = round((112.5 * fuel_consumed),2)
            prevailing_speed_range = [np.percentile(trip_data['Vehicle Speed Sensor'].values,75),
                                      np.percentile(trip_data['Vehicle Speed Sensor'].values,25)]

            trip_summary = {'Time_spent_on_road':time_spent_on_road, 'Average_speed':average_speed,'Maximum_speed':max_speed,
                            'Minimum_speed': min_speed, 'Distance_covered':distance_covered, 'Driving_Behaviour':driver_behaviour,
                            'Idle_engine_time': sum(idle_time), 'Fuel_consumed': fuel_consumed,'Estimated_fuel_cost':estimated_fuel_cost,
                            'Prevailing speed':prevailing_speed_range}

            return trip_summary
