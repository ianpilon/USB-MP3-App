'use client'

import { ArrowDownTrayIcon, CommandLineIcon, ArrowPathIcon } from '@heroicons/react/24/outline'

const steps = [
  {
    name: 'Download',
    description: 'Download the USB tool for your operating system',
    icon: ArrowDownTrayIcon,
  },
  {
    name: 'Copy to USB',
    description: 'Copy the tool to your USB drive',
    icon: CommandLineIcon,
  },
  {
    name: 'Start syncing',
    description: 'Run the tool to start syncing your music',
    icon: ArrowPathIcon,
  },
]

export default function DownloadSection() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-3xl text-center">
        <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
          Download USB Tool
        </h2>
        <p className="mx-auto mt-4 max-w-xl text-base text-gray-500">
          Download our USB tool to sync your music to any USB drive. No installation required.
        </p>
      </div>

      <div className="mx-auto mt-16 max-w-2xl sm:mt-20">
        <div className="grid grid-cols-1 gap-y-8 text-center sm:grid-cols-3 sm:gap-12">
          {steps.map((step) => (
            <div key={step.name}>
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-100">
                <step.icon className="h-8 w-8 text-indigo-600" aria-hidden="true" />
              </div>
              <h3 className="mt-6 text-base font-semibold leading-7 text-gray-900">{step.name}</h3>
              <p className="mt-2 text-sm text-gray-500">{step.description}</p>
            </div>
          ))}
        </div>

        <div className="mt-16 flex flex-col items-center gap-8">
          <button
            type="button"
            onClick={() => window.location.href = '/download/mac'}
            className="rounded-md bg-indigo-600 px-8 py-4 text-lg font-semibold text-white shadow-sm hover:bg-indigo-500"
          >
            Download for macOS
          </button>
          <p className="text-sm text-gray-500">
            Windows and Linux versions coming soon
          </p>
        </div>
      </div>
    </div>
  )
}
