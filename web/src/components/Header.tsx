'use client';

import { Bell } from 'lucide-react';

interface HeaderProps {
  title?: string;
}

export default function Header({ title }: HeaderProps) {
  return (
    <header className="bg-[#F26522] px-6 py-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-white">
            Occupational Certificate: Software Engineer 119458
          </p>
        </div>

        <div className="flex items-center gap-4">
          {/* Notifications */}
          <button className="relative p-2 text-white hover:bg-orange-600 rounded-full">
            <Bell size={20} />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>

          {/* User */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white text-[#F26522] rounded-full flex items-center justify-center font-semibold">
              AU
            </div>
            <div className="text-right">
              <p className="text-sm font-medium text-white">Admin User</p>
              <p className="text-xs text-white">Admin</p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
