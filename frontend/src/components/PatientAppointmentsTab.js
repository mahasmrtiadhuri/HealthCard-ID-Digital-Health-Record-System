import React from 'react';
import { Calendar, Clock, Info } from 'lucide-react';

// Patient Appointments Tab
export function PatientAppointmentsTab({ patientDetails, darkMode }) {
  const getStatusColor = (status) => {
    switch (status) {
      case 'scheduled': return 'bg-blue-100 text-blue-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'canceled': return 'bg-red-100 text-red-800';
      case 'rescheduled': return 'bg-yellow-100 text-yellow-800';
      case 'no_show': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const sortedAppointments = patientDetails.appointments.sort((a, b) => 
    new Date(b.appointment_date) - new Date(a.appointment_date)
  );

  const upcomingAppointments = sortedAppointments.filter(apt => 
    new Date(apt.appointment_date) >= new Date() && apt.status === 'scheduled'
  );

  const pastAppointments = sortedAppointments.filter(apt => 
    new Date(apt.appointment_date) < new Date() || apt.status !== 'scheduled'
  );

  return (
    <div className="space-y-6">
      {/* Upcoming Appointments */}
      <div>
        <h3 className={`text-lg font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-800'}`}>
          Upcoming Appointments ({upcomingAppointments.length})
        </h3>
        
        {upcomingAppointments.length === 0 ? (
          <div className={`text-center py-6 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
            <Calendar className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p>No upcoming appointments scheduled.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {upcomingAppointments.map((appointment) => (
              <AppointmentCard 
                key={appointment.id} 
                appointment={appointment} 
                darkMode={darkMode}
                getStatusColor={getStatusColor}
                isUpcoming={true}
              />
            ))}
          </div>
        )}
      </div>

      {/* Past Appointments */}
      <div>
        <h3 className={`text-lg font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-800'}`}>
          Past Appointments ({pastAppointments.length})
        </h3>
        
        {pastAppointments.length === 0 ? (
          <div className={`text-center py-6 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
            <Calendar className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p>No past appointments found.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {pastAppointments.slice(0, 10).map((appointment) => (
              <AppointmentCard 
                key={appointment.id} 
                appointment={appointment} 
                darkMode={darkMode}
                getStatusColor={getStatusColor}
                isUpcoming={false}
              />
            ))}
            {pastAppointments.length > 10 && (
              <p className={`text-sm text-center ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                Showing 10 most recent appointments of {pastAppointments.length} total
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function AppointmentCard({ appointment, darkMode, getStatusColor, isUpcoming }) {
  return (
    <div className={`p-4 border rounded-lg ${
      darkMode ? 'border-gray-600' : 'border-gray-200'
    } ${isUpcoming ? (darkMode ? 'bg-blue-900 bg-opacity-20' : 'bg-blue-50') : ''}`}>
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-4 mb-2">
            <h4 className={`font-semibold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
              {appointment.doctor_name ? `Dr. ${appointment.doctor_name}` : 'Doctor'}
            </h4>
            <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(appointment.status)}`}>
              {appointment.status.replace('_', ' ')}
            </span>
            {isUpcoming && (
              <span className="px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-800">
                Upcoming
              </span>
            )}
          </div>
          
          <div className="flex items-center space-x-4 text-sm mb-2">
            <div className="flex items-center">
              <Calendar className="h-4 w-4 mr-1 text-gray-400" />
              <span className={darkMode ? 'text-gray-300' : 'text-gray-600'}>
                {new Date(appointment.appointment_date).toLocaleDateString('en-US', {
                  weekday: 'short',
                  year: 'numeric',
                  month: 'short',
                  day: 'numeric'
                })}
              </span>
            </div>
            <div className="flex items-center">
              <Clock className="h-4 w-4 mr-1 text-gray-400" />
              <span className={darkMode ? 'text-gray-300' : 'text-gray-600'}>
                {appointment.appointment_time}
              </span>
            </div>
            <div className="flex items-center">
              <Info className="h-4 w-4 mr-1 text-gray-400" />
              <span className={darkMode ? 'text-gray-300' : 'text-gray-600'}>
                {appointment.appointment_type}
              </span>
            </div>
          </div>
          
          {appointment.reason && (
            <p className={`text-sm mt-2 ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
              <strong>Reason:</strong> {appointment.reason}
            </p>
          )}
          
          {appointment.notes && (
            <p className={`text-sm mt-1 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
              <strong>Notes:</strong> {appointment.notes}
            </p>
          )}

          {appointment.doctor_specialization && (
            <p className={`text-xs mt-2 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
              Specialization: {appointment.doctor_specialization}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}