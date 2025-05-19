use std::fmt;

use diesel::backend::Backend;
use diesel::deserialize::{self, FromSql, FromSqlRow};
use diesel::expression::AsExpression;
use diesel::serialize::{self, Output, ToSql};
use diesel::sql_types::BigInt;
use serde::{Deserialize, Serialize};

mod config;
mod profile;

pub use config::*;
pub use profile::*;

/// Newtype to allow postgres to work with u64 types because these are used a
/// lot in the discord API
///
/// Ideally this type never gets seen in model APIs and is only used internally
///
/// Technically discord snowflake types are strings, not u64, but for some
/// reason all the API libraries present them as u64
///
/// Agony
#[derive(
	AsExpression,
	Copy,
	Clone,
	Debug,
	Deserialize,
	Eq,
	PartialEq,
	FromSqlRow,
	Hash,
	Ord,
	PartialOrd,
	Serialize,
)]
#[diesel(sql_type = BigInt)]
#[repr(transparent)]
pub struct PgU64(pub u64);

impl fmt::Display for PgU64 {
	fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result { write!(f, "{}", self.0) }
}

impl AsRef<u64> for PgU64 {
	fn as_ref(&self) -> &u64 { &self.0 }
}

impl From<u64> for PgU64 {
	fn from(value: u64) -> Self { Self(value) }
}

impl From<PgU64> for u64 {
	fn from(value: PgU64) -> Self { value.0 }
}

impl<DB> FromSql<BigInt, DB> for PgU64
where
	DB: Backend,
	i64: FromSql<BigInt, DB>,
{
	fn from_sql(bytes: DB::RawValue<'_>) -> deserialize::Result<Self> {
		let i64_ = i64::from_sql(bytes)?;

		// We *want* to lose the sign
		#[allow(clippy::cast_sign_loss)]
		Ok(PgU64(i64_ as u64))
	}
}

impl<DB> ToSql<BigInt, DB> for PgU64
where
	DB: Backend,
	i64: ToSql<BigInt, DB>,
{
	fn to_sql<'b>(&'b self, out: &mut Output<'b, '_, DB>) -> serialize::Result {
		let i64_ref = unsafe { &*(&raw const self.0).cast::<i64>() };

		i64_ref.to_sql(out)
	}
}
