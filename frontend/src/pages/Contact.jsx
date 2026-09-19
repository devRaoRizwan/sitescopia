import { useState } from 'react'
import { useSeo } from '../seo'
import PageHeader from '../components/PageHeader'
import { CONTACT_EMAIL, buildBody, openGmail } from '../gmail'

const SUBJECTS = [
  'General question',
  'Bug report',
  'False positive in a scan',
  'Feature request',
  'Partnership or advertising',
]

const MESSAGE_MAX = 2000
const MESSAGE_MIN = 10

export default function Contact() {
  useSeo({
    title: 'Contact Us',
    description:
      "Questions, bug reports or a scan that got something wrong. Write to the team behind SiteScopia and we will get back to you.",
    path: '/contact',
  })

  const [form, setForm] = useState({ name: '', subject: SUBJECTS[0], message: '' })
  const [opened, setOpened] = useState(null)

  const update = (field) => (event) => setForm({ ...form, [field]: event.target.value })

  const ready = form.message.trim().length >= MESSAGE_MIN

  const compose = (event) => {
    event.preventDefault()
    if (!ready) return
    const payload = {
      subject: `[SiteScopia] ${form.subject}`,
      body: buildBody(form),
    }
    setOpened(openGmail(payload))
  }

  return (
    <>
      <PageHeader
        eyebrow="Contact"
        title="Get in touch"
        lead="Questions, bug reports, or a scan that got something wrong. We read everything."
      />

      <section className="section">
        <div className="shell contact-layout">
          <form className="contact-form" onSubmit={compose}>
            <h2 className="sr-only">Send us a message</h2>
            {opened && (
              <div className="notice notice-good">
                <strong>Your email is opening with the message ready.</strong>
                <span>
                  Nothing has been sent yet. Review it and press send. If nothing opened, use the
                  address below.
                </span>
              </div>
            )}

            <label className="field">
              <span>Your name</span>
              <input
                type="text"
                value={form.name}
                onChange={update('name')}
                maxLength={120}
                placeholder="So we know who we are replying to"
              />
            </label>

            <label className="field">
              <span>Topic</span>
              <select value={form.subject} onChange={update('subject')}>
                {SUBJECTS.map((subject) => (
                  <option key={subject}>{subject}</option>
                ))}
              </select>
            </label>

            <label className="field">
              <span>Message</span>
              <textarea
                value={form.message}
                onChange={update('message')}
                required
                minLength={MESSAGE_MIN}
                maxLength={MESSAGE_MAX}
                rows={8}
                placeholder="If this is about a scan, include the URL you analyzed."
              />
              <small>
                {form.message.length}/{MESSAGE_MAX} | at least {MESSAGE_MIN} characters
              </small>
            </label>

            <button type="submit" className="primary-button" disabled={!ready}>
              Open email
            </button>

            <p className="form-note">
              This opens your email with the message ready. Nothing is sent until you press send,
              and nothing is stored on our servers.
            </p>

            <div className="direct-contact">
              <span>Or write to us directly</span>
              <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>
            </div>
          </form>

          <aside className="contact-side">
            <section className="side-card">
              <h3>Reporting a bad scan</h3>
              <p>
                Include the exact URL and what you expected. Sites behind a bot challenge, or
                pages that build their content with JavaScript, are the two most common causes of
                a report that looks wrong.
              </p>
            </section>

            <section className="side-card">
              <h3>Why your email opens</h3>
              <p>
                The message is composed in your own mail app, so it arrives from your real address
                and you keep a copy in your sent folder. On phones the Gmail app opens directly; on
                desktop it opens Gmail on the web in a new tab.
              </p>
            </section>

            <section className="side-card">
              <h3>Security issues</h3>
              <p>
                Found a vulnerability in SiteScopia? Pick "Bug report" and we will reply before
                any public disclosure.
              </p>
            </section>
          </aside>
        </div>
      </section>
    </>
  )
}
