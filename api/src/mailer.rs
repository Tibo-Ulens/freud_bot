use lettre::message::Mailbox;
use lettre::transport::smtp::authentication::Credentials;
use lettre::{Address, Message, SmtpTransport, Transport};
use tokio::sync::mpsc;

use crate::Error;
use crate::models::profile::PendingProfile;

/// A basic interface to send email messages
#[derive(Clone, Debug)]
pub struct Mailer {
	from:       Address,
	send_queue: mpsc::Sender<Message>,
}

impl Mailer {
	/// Create a new mailer
	#[must_use]
	pub fn new(sender: Address, password: String) -> Self {
		let (tx, rx) = mpsc::channel(256);

		tokio::spawn(Self::start_smtp_sender(
			rx,
			sender.clone(),
			String::from("smtp.gmail.com"),
			password,
		));

		Self { from: sender, send_queue: tx }
	}

	/// Try to build an email [`Message`]
	///
	/// # Errors
	/// Fails if the receiver or body cannot be parsed
	pub fn try_build_message(
		&self,
		receiver: impl TryInto<Mailbox, Error = impl Into<Error>>,
		subject: &str,
		body: &str,
	) -> Result<Message, Error> {
		Ok(Message::builder()
			.from(Mailbox::new(None, self.from.clone()))
			.to(receiver.try_into().map_err(Into::into)?)
			.subject(subject)
			.body(body.to_string())?)
	}

	/// Try to send a message
	///
	/// # Errors
	/// Fails if the mail queue is full
	#[instrument(skip_all)]
	pub fn try_send(&self, message: Message) -> Result<(), Error> {
		Ok(self.send_queue.try_send(message)?)
	}

	/// Send a message and block if the mail queue is full
	///
	/// # Errors
	/// Fails if the other end of the mail queue was unexpectedly closed
	#[instrument(skip_all)]
	pub async fn send(&self, message: Message) -> Result<(), Error> {
		Ok(self.send_queue.send(message).await?)
	}

	/// Start an infinitely looping smtp sender thread
	#[instrument(skip(rx, password))]
	async fn start_smtp_sender(
		mut rx: mpsc::Receiver<Message>,
		address: Address,
		server: String,
		password: String,
	) {
		let transport = SmtpTransport::starttls_relay(&server)
			.expect("STARTTLS ERROR")
			.credentials(Credentials::new(address.to_string(), password))
			.build();

		match transport.test_connection() {
			Ok(_) => (),
			Err(e) => panic!("SMTP CONNECTION FAILED: {e:?}"),
		}

		while let Some(mail) = rx.recv().await {
			match transport.send(&mail) {
				Ok(res) => info!("sent email: {res:?}"),
				Err(e) => error!("error sending email: {e:?}"),
			}

			tokio::time::sleep(std::time::Duration::from_secs(1)).await;
		}
	}

	/// Send out a verification link email
	#[instrument(skip(self))]
	pub(crate) async fn send_verification_link(
		&self,
		profile: &PendingProfile,
		confirmation_token: &str,
		base_url: &str,
	) -> Result<(), Error> {
		let confirmation_url = format!("{base_url}/verify/{confirmation_token}");

		let mail = self.try_build_message(
			profile,
			"Verify Your Email",
			&format!("Please verify your email by going to {confirmation_url}"),
		)?;

		self.send(mail).await?;

		info!("sent verification email to {}", profile.email);

		Ok(())
	}
}
