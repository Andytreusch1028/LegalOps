import React from 'react'
import { motion } from 'framer-motion'
import { Upload, FileText, Download, Eye, Trash2 } from 'lucide-react'

export const DocumentsPage: React.FC = () => {
  const documents = [
    {
      id: 1,
      name: 'Articles of Organization - Acme LLC',
      type: 'PDF',
      size: '2.4 MB',
      uploaded: '2023-12-01',
      entity: 'Acme LLC'
    },
    {
      id: 2,
      name: 'Operating Agreement - Acme LLC',
      type: 'PDF',
      size: '1.8 MB',
      uploaded: '2023-12-01',
      entity: 'Acme LLC'
    },
    {
      id: 3,
      name: 'Annual Report 2023 - Beta Corp',
      type: 'PDF',
      size: '3.2 MB',
      uploaded: '2023-11-15',
      entity: 'Beta Corporation'
    }
  ]

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold text-gradient mb-2">
            Documents
          </h1>
          <p className="text-white/70">
            Manage and organize your legal documents securely.
          </p>
        </div>
        <button className="btn-primary flex items-center gap-2">
          <Upload className="w-5 h-5" />
          Upload Document
        </button>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
        className="card"
      >
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/20">
                <th className="text-left py-4 px-2 text-white/80 font-medium">Name</th>
                <th className="text-left py-4 px-2 text-white/80 font-medium">Type</th>
                <th className="text-left py-4 px-2 text-white/80 font-medium">Size</th>
                <th className="text-left py-4 px-2 text-white/80 font-medium">Entity</th>
                <th className="text-left py-4 px-2 text-white/80 font-medium">Uploaded</th>
                <th className="text-left py-4 px-2 text-white/80 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((doc, index) => (
                <motion.tr
                  key={doc.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                  className="border-b border-white/10 hover:bg-white/5 transition-colors"
                >
                  <td className="py-4 px-2">
                    <div className="flex items-center gap-3">
                      <FileText className="w-5 h-5 text-red-400" />
                      <span className="text-white font-medium">{doc.name}</span>
                    </div>
                  </td>
                  <td className="py-4 px-2 text-white/70">{doc.type}</td>
                  <td className="py-4 px-2 text-white/70">{doc.size}</td>
                  <td className="py-4 px-2 text-white/70">{doc.entity}</td>
                  <td className="py-4 px-2 text-white/70">{doc.uploaded}</td>
                  <td className="py-4 px-2">
                    <div className="flex items-center gap-2">
                      <button 
                        className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors"
                        title="View document"
                        aria-label="View document"
                      >
                        <Eye className="w-4 h-4 text-white/70" />
                      </button>
                      <button 
                        className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors"
                        title="Download document"
                        aria-label="Download document"
                      >
                        <Download className="w-4 h-4 text-white/70" />
                      </button>
                      <button 
                        className="p-2 rounded-lg bg-red-500/20 hover:bg-red-500/30 transition-colors"
                        title="Delete document"
                        aria-label="Delete document"
                      >
                        <Trash2 className="w-4 h-4 text-red-400" />
                      </button>
                    </div>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  )
}
