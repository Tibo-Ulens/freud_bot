use deadpool_lapin::lapin::BasicProperties;
use deadpool_lapin::lapin::options::{BasicPublishOptions, QueueDeclareOptions};
use deadpool_lapin::lapin::types::FieldTable;
use serde::{Deserialize, Serialize};

use crate::AmqpConn;
use crate::error::Error;

/// A command instructing the receiver to verify a user with the given id
#[derive(Clone, Copy, Debug, Deserialize, Serialize)]
pub struct VerificationCommand<'s> {
	pub user_id: &'s [u8],
}

impl<'s> VerificationCommand<'s> {
	#[must_use]
	pub fn new(user_id: &'s [u8]) -> Self { Self { user_id } }

	pub async fn send(&self, conn: &AmqpConn) -> Result<(), Error> {
		let channel = conn.create_channel().await?;
		channel
			.queue_declare("verification", QueueDeclareOptions::default(), FieldTable::default())
			.await?;

		channel
			.basic_publish(
				"",
				"verification",
				BasicPublishOptions::default(),
				self.user_id,
				BasicProperties::default(),
			)
			.await?;

		Ok(())
	}
}
