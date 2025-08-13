import React from 'react';
import { Upload, FileText, Image, Download, Eye } from 'lucide-react';

// Patient Files Tab
export function PatientFilesTab({ patientDetails, darkMode }) {
  const getFileIcon = (fileType) => {
    if (fileType?.includes('image')) {
      return <Image className="h-5 w-5 text-blue-500" />;
    } else if (fileType?.includes('pdf')) {
      return <FileText className="h-5 w-5 text-red-500" />;
    }
    return <FileText className="h-5 w-5 text-gray-500" />;
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return 'N/A';
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
          Uploaded Files ({patientDetails.files.length})
        </h3>
      </div>

      {patientDetails.files.length === 0 ? (
        <div className={`text-center py-8 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
          <Upload className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p>No files uploaded yet.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {patientDetails.files.map((file) => (
            <div 
              key={file.id} 
              className={`p-4 border rounded-lg hover:shadow-md transition ${
                darkMode ? 'border-gray-600 hover:border-gray-500' : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 mt-1">
                  {getFileIcon(file.file_type)}
                </div>
                
                <div className="flex-1 min-w-0">
                  <h4 className={`font-medium text-sm ${darkMode ? 'text-white' : 'text-gray-800'} truncate`}>
                    {file.original_filename}
                  </h4>
                  
                  <div className="flex items-center space-x-2 mt-1">
                    <span className={`text-xs px-2 py-1 rounded ${
                      file.upload_type === 'medical_report' ? 'bg-blue-100 text-blue-700' :
                      file.upload_type === 'profile_image' ? 'bg-green-100 text-green-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {file.upload_type?.replace('_', ' ')}
                    </span>
                  </div>
                  
                  <div className={`text-xs mt-2 space-y-1 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                    <p>Size: {formatFileSize(file.file_size)}</p>
                    <p>Uploaded: {new Date(file.created_at).toLocaleDateString()}</p>
                    {file.file_type && (
                      <p>Type: {file.file_type.split('/')[1].toUpperCase()}</p>
                    )}
                  </div>
                  
                  {file.ai_summary && (
                    <div className={`mt-3 p-2 rounded text-xs ${
                      darkMode ? 'bg-gray-700 text-gray-300' : 'bg-gray-50 text-gray-700'
                    }`}>
                      <p className="font-medium mb-1">AI Summary:</p>
                      <p className="text-xs">{file.ai_summary}</p>
                    </div>
                  )}
                  
                  <div className="flex space-x-2 mt-3">
                    <button 
                      className={`flex items-center text-xs px-2 py-1 rounded hover:bg-blue-100 ${
                        darkMode ? 'text-blue-400 hover:bg-blue-900' : 'text-blue-600'
                      }`}
                      onClick={() => {
                        // Handle file view
                        console.log('View file:', file.id);
                      }}
                    >
                      <Eye className="h-3 w-3 mr-1" />
                      View
                    </button>
                    <button 
                      className={`flex items-center text-xs px-2 py-1 rounded hover:bg-gray-100 ${
                        darkMode ? 'text-gray-400 hover:bg-gray-700' : 'text-gray-600'
                      }`}
                      onClick={() => {
                        // Handle file download
                        console.log('Download file:', file.id);
                      }}
                    >
                      <Download className="h-3 w-3 mr-1" />
                      Download
                    </button>
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