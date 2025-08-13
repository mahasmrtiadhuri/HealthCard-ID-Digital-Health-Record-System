import React, { useState } from 'react';
import { 
  User, 
  FileText, 
  Pill, 
  Calendar, 
  Upload, 
  ChevronRight, 
  Settings 
} from 'lucide-react';
import { PatientOverviewTab } from './PatientOverviewTab';
import { PatientRecordsTab } from './PatientRecordsTab';
import { PatientPrescriptionsTab } from './PatientPrescriptionsTab';
import { PatientAppointmentsTab } from './PatientAppointmentsTab';
import { PatientFilesTab } from './PatientFilesTab';

// Patient Detail View Component for Doctors
export function PatientDetailView({ patient, patientDetails, darkMode, onBack, onRefresh }) {
  const [activeTab, setActiveTab] = useState("overview");
  const [showMultiPrescriptionForm, setShowMultiPrescriptionForm] = useState(false);

  const tabItems = [
    { id: "overview", label: "Overview", icon: <User className="h-4 w-4" /> },
    { id: "records", label: "Medical Records", icon: <FileText className="h-4 w-4" /> },
    { id: "prescriptions", label: "Prescriptions", icon: <Pill className="h-4 w-4" /> },
    { id: "appointments", label: "Appointments", icon: <Calendar className="h-4 w-4" /> },
    { id: "files", label: "Files", icon: <Upload className="h-4 w-4" /> },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className={`p-6 rounded-xl shadow-lg ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
        <div className="flex items-center justify-between mb-4">
          <button
            onClick={onBack}
            className={`flex items-center text-blue-600 hover:text-blue-700 ${darkMode ? 'text-blue-400 hover:text-blue-300' : ''}`}
          >
            <ChevronRight className="h-4 w-4 mr-1 transform rotate-180" />
            Back to Patient List
          </button>
          <button
            onClick={onRefresh}
            className={`p-2 rounded-lg ${darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`}
          >
            <Settings className="h-4 w-4" />
          </button>
        </div>

        <div className="flex items-center space-x-4">
          <div className={`w-16 h-16 rounded-full flex items-center justify-center ${darkMode ? 'bg-gray-700' : 'bg-gray-100'}`}>
            <User className={`h-8 w-8 ${darkMode ? 'text-gray-300' : 'text-gray-600'}`} />
          </div>
          <div>
            <h1 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
              {patientDetails.patient_info.name}
            </h1>
            <p className={`${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
              {patientDetails.patient_info.email}
            </p>
            {patientDetails.patient_info.phone && (
              <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                📞 {patientDetails.patient_info.phone}
              </p>
            )}
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-4 gap-4 mt-6">
          <div className={`p-3 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-50'}`}>
            <div className="text-center">
              <p className={`text-lg font-bold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                {patientDetails.stats.total_records}
              </p>
              <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Records</p>
            </div>
          </div>
          <div className={`p-3 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-50'}`}>
            <div className="text-center">
              <p className={`text-lg font-bold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                {patientDetails.stats.total_prescriptions}
              </p>
              <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Prescriptions</p>
            </div>
          </div>
          <div className={`p-3 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-50'}`}>
            <div className="text-center">
              <p className={`text-lg font-bold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                {patientDetails.stats.total_appointments}
              </p>
              <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Appointments</p>
            </div>
          </div>
          <div className={`p-3 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-50'}`}>
            <div className="text-center">
              <p className={`text-lg font-bold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                {patientDetails.stats.total_files}
              </p>
              <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Files</p>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className={`p-6 rounded-xl shadow-lg ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
        <div className="flex space-x-1 mb-6">
          {tabItems.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition ${
                activeTab === tab.id
                  ? 'bg-blue-600 text-white'
                  : darkMode
                    ? 'text-gray-300 hover:bg-gray-700'
                    : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              {tab.icon}
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {activeTab === "overview" && (
          <PatientOverviewTab patientDetails={patientDetails} darkMode={darkMode} />
        )}
        {activeTab === "records" && (
          <PatientRecordsTab patientDetails={patientDetails} darkMode={darkMode} />
        )}
        {activeTab === "prescriptions" && (
          <PatientPrescriptionsTab 
            patientDetails={patientDetails} 
            darkMode={darkMode}
            showMultiPrescriptionForm={showMultiPrescriptionForm}
            setShowMultiPrescriptionForm={setShowMultiPrescriptionForm}
            onRefresh={onRefresh}
          />
        )}
        {activeTab === "appointments" && (
          <PatientAppointmentsTab patientDetails={patientDetails} darkMode={darkMode} />
        )}
        {activeTab === "files" && (
          <PatientFilesTab patientDetails={patientDetails} darkMode={darkMode} />
        )}
      </div>
    </div>
  );
}