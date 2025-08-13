import React from 'react';

// Patient Overview Tab
export function PatientOverviewTab({ patientDetails, darkMode }) {
  const patient = patientDetails.patient_info;
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Basic Info */}
      <div className={`p-4 rounded-lg border ${darkMode ? 'border-gray-600' : 'border-gray-200'}`}>
        <h3 className={`font-semibold mb-3 ${darkMode ? 'text-white' : 'text-gray-800'}`}>Basic Information</h3>
        <div className="space-y-2">
          <InfoRow label="Age" value={patient.age || "N/A"} darkMode={darkMode} />
          <InfoRow label="Gender" value={patient.gender || "N/A"} darkMode={darkMode} />
          <InfoRow label="Blood Group" value={patient.blood_group || "N/A"} darkMode={darkMode} />
          <InfoRow label="Weight" value={patient.weight ? `${patient.weight} kg` : "N/A"} darkMode={darkMode} />
          <InfoRow label="Height" value={patient.height ? `${patient.height} cm` : "N/A"} darkMode={darkMode} />
        </div>
      </div>

      {/* Medical Info */}
      <div className={`p-4 rounded-lg border ${darkMode ? 'border-gray-600' : 'border-gray-200'}`}>
        <h3 className={`font-semibold mb-3 ${darkMode ? 'text-white' : 'text-gray-800'}`}>Medical Information</h3>
        <div className="space-y-3">
          <div>
            <label className={`text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>Allergies</label>
            <div className="flex flex-wrap gap-1 mt-1">
              {patient.allergies && patient.allergies.length > 0 ? (
                patient.allergies.map((allergy, index) => (
                  <span key={index} className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded">
                    {allergy}
                  </span>
                ))
              ) : (
                <span className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>None reported</span>
              )}
            </div>
          </div>

          <div>
            <label className={`text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>Chronic Conditions</label>
            <div className="flex flex-wrap gap-1 mt-1">
              {patient.chronic_conditions && patient.chronic_conditions.length > 0 ? (
                patient.chronic_conditions.map((condition, index) => (
                  <span key={index} className="bg-orange-100 text-orange-800 text-xs px-2 py-1 rounded">
                    {condition}
                  </span>
                ))
              ) : (
                <span className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>None reported</span>
              )}
            </div>
          </div>

          <div>
            <label className={`text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>Current Medications</label>
            <div className="flex flex-wrap gap-1 mt-1">
              {patient.current_medications && patient.current_medications.length > 0 ? (
                patient.current_medications.map((medication, index) => (
                  <span key={index} className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                    {medication}
                  </span>
                ))
              ) : (
                <span className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>None reported</span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Insurance Details */}
      <div className={`p-4 rounded-lg border ${darkMode ? 'border-gray-600' : 'border-gray-200'} md:col-span-2`}>
        <h3 className={`font-semibold mb-3 ${darkMode ? 'text-white' : 'text-gray-800'}`}>🛡️ Insurance Details</h3>
        {patient.insurance_details ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <InfoRow label="Provider" value={patient.insurance_details.provider || "N/A"} darkMode={darkMode} />
            <InfoRow label="Policy Number" value={patient.insurance_details.policy_number || "N/A"} darkMode={darkMode} />
            <InfoRow label="Plan Type" value={patient.insurance_details.plan_type || "N/A"} darkMode={darkMode} />
            <InfoRow label="Coverage Amount" value={patient.insurance_details.coverage_amount || "N/A"} darkMode={darkMode} />
            <InfoRow label="Expiry Date" value={patient.insurance_details.expiry_date || "N/A"} darkMode={darkMode} />
            <div className="md:col-span-3">
              <InfoRow label="Notes" value={patient.insurance_details.notes || "N/A"} darkMode={darkMode} />
            </div>
          </div>
        ) : (
          <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>No insurance information available</p>
        )}
      </div>
    </div>
  );
}

function InfoRow({ label, value, darkMode }) {
  return (
    <div className="flex justify-between">
      <span className={`text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>{label}:</span>
      <span className={`text-sm ${darkMode ? 'text-gray-200' : 'text-gray-800'}`}>{value}</span>
    </div>
  );
}