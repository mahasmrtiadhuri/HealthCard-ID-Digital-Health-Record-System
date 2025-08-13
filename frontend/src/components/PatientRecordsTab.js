import React from 'react';
import { FileText } from 'lucide-react';

// Patient Records Tab
export function PatientRecordsTab({ patientDetails, darkMode }) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
          Medical Records ({patientDetails.medical_records.length})
        </h3>
      </div>

      {patientDetails.medical_records.length === 0 ? (
        <div className={`text-center py-8 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
          <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p>No medical records found.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {patientDetails.medical_records.map((record) => (
            <div key={record.id} className={`p-4 border rounded-lg ${darkMode ? 'border-gray-600' : 'border-gray-200'}`}>
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h4 className={`font-medium ${darkMode ? 'text-white' : 'text-gray-800'}`}>{record.title}</h4>
                  <p className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'} mt-1`}>
                    {record.description}
                  </p>
                  <div className="flex items-center space-x-4 mt-2 text-xs">
                    <span className={`px-2 py-1 rounded ${
                      record.record_type === 'report' ? 'bg-blue-100 text-blue-800' :
                      record.record_type === 'prescription' ? 'bg-green-100 text-green-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {record.record_type}
                    </span>
                    <span className={`${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                      {new Date(record.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}