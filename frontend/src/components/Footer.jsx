import React from 'react'
import { Github, Twitter, Linkedin, Mail, Heart } from 'lucide-react'

const Footer = () => {
  return (
    <footer className="relative bg-gov-navy border-t border-gov-blue/20 py-12 px-6">
      <div className="max-w-7xl mx-auto">
        <div className="grid md:grid-cols-3 gap-12 mb-8">
          {/* Brand */}
          <div>
            <h3 className="text-2xl font-bold font-heading mb-4">
              <span className="text-gradient">City Governance AI</span>
            </h3>
            <p className="text-neutral-offWhite/80 text-sm leading-relaxed">
              Multi-agent autonomous system orchestrating intelligent city governance 
              with transparency, accountability, and human oversight.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="font-bold mb-4 text-accent-gold">Quick Links</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <a href="#agents" className="text-neutral-offWhite/80 hover:text-accent-gold transition-colors">
                  Department Agents
                </a>
              </li>
              <li>
                <a href="#coordination" className="text-neutral-offWhite/80 hover:text-accent-gold transition-colors">
                  Coordination System
                </a>
              </li>
              <li>
                <a href="#transparency" className="text-neutral-offWhite/80 hover:text-accent-gold transition-colors">
                  Transparency Vault
                </a>
              </li>
              <li>
                <a href="#workflow" className="text-neutral-offWhite/80 hover:text-accent-gold transition-colors">
                  Decision Workflow
                </a>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="font-bold mb-4 text-accent-gold">Connect</h4>
            <div className="flex gap-4">
              <SocialLink href="#" icon={<Github size={20} />} label="GitHub" />
              <SocialLink href="#" icon={<Twitter size={20} />} label="Twitter" />
              <SocialLink href="#" icon={<Linkedin size={20} />} label="LinkedIn" />
              <SocialLink href="mailto:contact@citygovernance.ai" icon={<Mail size={20} />} label="Email" />
            </div>
            <p className="text-neutral-offWhite/70 text-xs mt-6">
              <strong>License:</strong> Apache 2.0<br />
              <strong>Version:</strong> 2.0.0
            </p>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-gov-blue/20 text-center">
          <p className="text-sm text-neutral-offWhite/80 flex items-center justify-center gap-2">
            Built with <Heart size={14} className="text-accent-gold fill-current" /> for urban innovation
          </p>
          <p className="text-xs text-neutral-offWhite/60 mt-2">
            © 2026 City Governance AI. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  )
}

const SocialLink = ({ href, icon, label }) => (
  <a
    href={href}
    aria-label={label}
    className="w-10 h-10 professional-card rounded-lg flex items-center justify-center hover:shadow-gold-glow hover:text-accent-gold transition-all text-gov-blue"
  >
    {icon}
  </a>
)

export default Footer
