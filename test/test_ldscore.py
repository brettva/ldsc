import ldscore.ldscore as ld
import unittest
import bitarray as ba
import numpy as np
import nose
import pandas as pd
import ldscore.parse as ps
from nose_parameterized import parameterized as param


##########################################################################################
#                                  MISC FUNCTIONS                                        #
##########################################################################################


@param([
	(np.arange(1,6),5,np.zeros(5)),
	(np.arange(1,6),0,np.arange(0,5)),
	((1,4,6,7,7,8),2,(0,1,1,2,2,2))])
def test_getBlockLefts(coords, max_dist, correct):
	assert np.all(ld.getBlockLefts(coords, max_dist) == correct)

@param([
	((0,0,0,0,0),(5,5,5,5,5)),
	((0,1,2,3,4,5), (1,2,3,4,5,6)),
	((0,0,2,2), (2,2,4,4))
	])
def test_block_left_to_right(block_left, correct_answer):
	block_right = ld.block_left_to_right(block_left)
	print block_right - correct_answer
	assert np.all(block_right == correct_answer)


##########################################################################################
#                                    BED PARSER                                          #
##########################################################################################


class test_bed(unittest.TestCase):
 
 	def setUp(self):
 		self.M = 8
 		self.N = 5
		self.bim = ps.PlinkBIMFile('test/plink_test/plink.bim')

 	def test_bed(self):
 		bed = ld.PlinkBEDFile('test/plink_test/plink.bed', self.N, self.bim)
 		# remove three monomorphic SNPs
 		print bed.geno
		print bed.m
 		assert bed.m == 4
 		# no individuals removed	
 		print bed.n	
 		assert self.N == bed.n
 		# 5 indivs * 4 polymorphic SNPs
 		print len(bed.geno)
 		assert len(bed.geno) == 64
 		print bed.freq
 		correct = np.array([0.59999999999999998, 0.59999999999999998, 0.625, 0.625])
 		assert np.all(bed.freq == correct)
 				
 	def test_filter_snps(self):
 		keep_snps = [1,4]
 		bed = ld.PlinkBEDFile('test/plink_test/plink.bed', self.N, self.bim,
 			keep_snps=keep_snps)
 		assert bed.m == 1
 		assert bed.n == 5
  	# pad bits are initialized with random memory --> can't test them
 		assert bed.geno[0:10] == ba.bitarray('0001011111')
 		
 	def test_filter_indivs(self):
 		keep_indivs = [0,1]
 		bed = ld.PlinkBEDFile('test/plink_test/plink.bed', self.N, self.bim, 
 			keep_indivs=keep_indivs)
 		assert bed.m == 2
 		assert bed.n == 2
 		# pad bits are initialized with random memory --> can't test them
 		assert bed.geno[0:4] == ba.bitarray('0001')
 		assert bed.geno[8:12] == ba.bitarray('0001')
	
	def test_filter_indivs_and_snps(self):
		keep_indivs = [0,1]
		keep_snps = [1,5]
		bed = ld.PlinkBEDFile('test/plink_test/plink.bed', self.N, self.bim, 
			keep_snps=keep_snps, keep_indivs=keep_indivs)
		assert bed.m == 1
		assert bed.n == 2
		print bed.geno
		assert bed.geno[0:4] == ba.bitarray('0001')
	
	@nose.tools.raises(ValueError)
	def test_bad_filename(self):
		bed = ld.PlinkBEDFile('test/plink_test/plink.bim', 9, self.bim)
	
	@nose.tools.raises(ValueError)	
	def test_nextSNPs_errors1(self):
		bed = ld.PlinkBEDFile('test/plink_test/plink.bed', self.N, self.bim)
		bed.nextSNPs(0)
	
	@nose.tools.raises(ValueError)	
	def test_nextSNPs_errors2(self):
		bed = ld.PlinkBEDFile('test/plink_test/plink.bed', self.N, self.bim)
		bed.nextSNPs(5)
				
	@param.expand([([1]),([2]),([3])])
	def test_nextSNPs(self, b):
		bed = ld.PlinkBEDFile('test/plink_test/plink.bed', self.N, self.bim)
		x = bed.nextSNPs(b)
		print x
		print np.std(x,axis=0)
		assert x.shape == (5,b)
		assert np.all(np.abs(np.mean(x, axis=0)) < 0.01)
		assert np.all(np.abs(np.std(x, axis=0) - 1) < 0.01)		

	def test_nextSNPs_maf_ref(self):
		b = 4
		bed = ld.PlinkBEDFile('test/plink_test/plink.bed', self.N, self.bim)
		x = bed.nextSNPs(b)
		bed._currentSNP -= b
		y = bed.nextSNPs(b, minorRef=True)
		assert np.all(x == -y)


