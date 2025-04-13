'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { CloudArrowUpIcon } from '@heroicons/react/24/outline'

export default function UploadForm() {
  const [files, setFiles] = useState<File[]>([])
  const [uploading, setUploading] = useState(false)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles(prev => [...prev, ...acceptedFiles])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/mpeg': ['.mp3']
    }
  })

  const uploadFiles = async () => {
    setUploading(true)
    try {
      for (const file of files) {
        const formData = new FormData()
        formData.append('file', file)
        
        const token = await fetch('https://dj-usb-server-usb-mp3-app.onrender.com/auth/token', {
          method: 'POST'
        }).then(r => r.json())
        
        await fetch('https://dj-usb-server-usb-mp3-app.onrender.com/upload', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token.access_token}`
          },
          body: formData
        })
      }
      setFiles([])
      alert('Upload complete!')
    } catch (error) {
      console.error('Upload failed:', error)
      alert('Upload failed. Please try again.')
    }
    setUploading(false)
  }

  return (
    <>
      <div className="mt-8">
        <div {...getRootProps()} className="flex justify-center rounded-lg border border-dashed border-gray-900/25 px-6 py-10">
          <div className="text-center">
            <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-300" aria-hidden="true" />
            <div className="mt-4 flex text-sm leading-6 text-gray-600">
              <input {...getInputProps()} />
              {isDragActive ? (
                <p>Drop the files here ...</p>
              ) : (
                <p>Drag &apos;n&apos; drop MP3 files here, or click to select files</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {files.length > 0 && (
        <div className="mt-8">
          <h3 className="text-lg font-medium text-gray-900">Selected Files</h3>
          <ul className="mt-4 divide-y divide-gray-100">
            {files.map((file, i) => (
              <li key={i} className="py-4">
                <div className="flex items-center justify-between">
                  <p className="truncate text-sm font-medium text-gray-900">{file.name}</p>
                  <button
                    type="button"
                    onClick={() => setFiles(files.filter((_, index) => index !== i))}
                    className="ml-4 text-sm font-medium text-indigo-600 hover:text-indigo-500"
                  >
                    Remove
                  </button>
                </div>
              </li>
            ))}
          </ul>

          <button
            type="button"
            onClick={uploadFiles}
            disabled={uploading}
            className="mt-8 rounded-md bg-indigo-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
          >
            {uploading ? 'Uploading...' : 'Upload Files'}
          </button>
        </div>
      )}
    </>
  )
}
