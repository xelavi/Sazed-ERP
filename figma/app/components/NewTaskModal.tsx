import { X, Calendar, Tag, Paperclip, FileText, MapPin, User as UserIcon } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';

interface NewTaskModalProps {
  open: boolean;
  onClose: () => void;
}

export function NewTaskModal({ open, onClose }: NewTaskModalProps) {
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px] p-0 gap-0">
        {/* Header */}
        <DialogHeader className="px-6 pt-5 pb-3 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <DialogTitle className="text-lg font-medium text-gray-900">
              New task
            </DialogTitle>
            <div className="flex items-center gap-2">
              <button className="text-xs px-3 py-1.5 hover:bg-gray-100 rounded transition-colors text-gray-700">
                Full screen
              </button>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 transition-colors p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>
        </DialogHeader>

        {/* Content */}
        <div className="px-6 pb-6 space-y-4 max-h-[70vh] overflow-y-auto">
          {/* Helper Text */}
          <div className="pt-4">
            <button className="text-sm text-gray-500 hover:text-gray-700 underline">
              Click here to see relevant docs about this meeting
            </button>
          </div>

          {/* Meeting Info Section */}
          <div className="bg-gray-50 rounded-lg p-4 space-y-3">
            <div className="flex items-start gap-3">
              <span className="text-sm font-medium text-gray-700 min-w-[80px]">Meeting</span>
              <p className="text-sm text-gray-900">1:1 with Product Lead</p>
            </div>
            <div className="flex items-start gap-3">
              <span className="text-sm font-medium text-gray-700 min-w-[80px]">Date</span>
              <p className="text-sm text-gray-900">16:00 PM Dec 22 2025</p>
            </div>
            <div className="flex items-start gap-3">
              <span className="text-sm font-medium text-gray-700 min-w-[80px]">Location</span>
              <p className="text-sm text-gray-900">Online[Google Meeting :]</p>
            </div>
          </div>

          {/* Host Info */}
          <div className="flex items-center gap-2 py-2">
            <div className="w-6 h-6 rounded-full bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center">
              <UserIcon className="w-3 h-3 text-white" />
            </div>
            <p className="text-sm text-gray-700">
              <span className="font-medium">Alex Smith</span> is the host of this meeting 🥳
            </p>
          </div>

          {/* Task Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Task name
            </label>
            <input
              type="text"
              placeholder="Enter task name..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-sm"
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              placeholder="Add description..."
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-sm resize-none"
            />
          </div>

          {/* Attachments */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Attachments
            </label>

            {/* PDF Attachment Preview */}
            <div className="flex items-center gap-3 px-3 py-2.5 bg-white rounded-lg border border-gray-300 hover:border-gray-400 transition-colors">
              <div className="w-8 h-8 bg-red-500 rounded flex items-center justify-center flex-shrink-0">
                <FileText className="w-4 h-4 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  ASMobbin-pdf.pdf
                </p>
                <p className="text-xs text-gray-500">PDF · Download</p>
              </div>
            </div>
          </div>

          {/* Bottom Action Icons */}
          <div className="flex items-center gap-1 pt-2">
            <button className="p-2 hover:bg-gray-100 rounded transition-colors text-gray-600">
              <Paperclip className="w-4 h-4" />
            </button>
            <button className="p-2 hover:bg-gray-100 rounded transition-colors text-gray-600">
              <Calendar className="w-4 h-4" />
            </button>
            <button className="p-2 hover:bg-gray-100 rounded transition-colors text-gray-600">
              <Tag className="w-4 h-4" />
            </button>
            <button className="p-2 hover:bg-gray-100 rounded transition-colors text-gray-600">
              <MapPin className="w-4 h-4" />
            </button>
            <div className="flex-1"></div>
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
              <UserIcon className="w-4 h-4 text-white" />
            </div>
            <button className="text-xl text-gray-400 hover:text-gray-600 px-2">+</button>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-gray-200 flex justify-end">
          <button className="px-6 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-lg font-medium text-sm transition-colors">
            Create task
          </button>
        </div>
      </DialogContent>
    </Dialog>
  );
}