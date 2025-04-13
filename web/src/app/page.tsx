import Image from 'next/image'
import Link from 'next/link'
import { CloudArrowUpIcon, DevicePhoneMobileIcon, ArrowPathIcon } from '@heroicons/react/24/outline'

const features = [
  {
    name: 'Upload your music',
    description: 'Upload your MP3 files directly to our secure cloud storage.',
    icon: CloudArrowUpIcon,
  },
  {
    name: 'Sync to USB',
    description: 'Download our USB tool and sync your music to any USB drive.',
    icon: DevicePhoneMobileIcon,
  },
  {
    name: 'Always in sync',
    description: 'Your music stays in sync across all your USB drives automatically.',
    icon: ArrowPathIcon,
  },
]

export default function Home() {
  return (
    <main className="bg-white">
      {/* Hero section */}
      <div className="relative isolate px-6 pt-14 lg:px-8">
        <div className="mx-auto max-w-2xl py-32 sm:py-48 lg:py-56">
          <div className="text-center">
            <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
              Your music, anywhere you DJ
            </h1>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              Upload your music once, sync to any USB drive, and start DJing. No installations required.
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <Link
                href="/upload"
                className="rounded-md bg-indigo-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
              >
                Upload Music
              </Link>
              <Link href="/download" className="text-sm font-semibold leading-6 text-gray-900">
                Download USB Tool <span aria-hidden="true">→</span>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Feature section */}
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl lg:text-center">
          <h2 className="text-base font-semibold leading-7 text-indigo-600">Start DJing faster</h2>
          <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
            Everything you need to manage your DJ music
          </p>
        </div>
        <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-4xl">
          <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-10 lg:max-w-none lg:grid-cols-3 lg:gap-y-16">
            {features.map((feature) => (
              <div key={feature.name} className="relative pl-16">
                <dt className="text-base font-semibold leading-7 text-gray-900">
                  <div className="absolute left-0 top-0 flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-600">
                    <feature.icon className="h-6 w-6 text-white" aria-hidden="true" />
                  </div>
                  {feature.name}
                </dt>
                <dd className="mt-2 text-base leading-7 text-gray-600">{feature.description}</dd>
              </div>
            ))}
          </dl>
        </div>
      </div>
    </main>
  )
}
