import UploadForm from './upload-form'

export default function Upload() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-3xl">
        <h1 className="text-3xl font-bold tracking-tight text-gray-900">Upload Music</h1>
        <UploadForm />
      </div>
    </div>
  )
}
